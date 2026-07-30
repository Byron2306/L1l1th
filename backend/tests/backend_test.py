"""Backend tests for Lilith app - voice, image, chat endpoints."""
import os
import base64
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fallback: read from /app/frontend/.env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------- Voice ----------
class TestVoice:
    def test_voice_list_has_preview_url(self, client):
        r = client.get(f"{BASE_URL}/api/voice/list", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "voices" in data and isinstance(data["voices"], list)
        assert len(data["voices"]) > 0
        # at least one voice has preview_url
        with_preview = [v for v in data["voices"] if isinstance(v.get("preview_url"), str) and v.get("preview_url")]
        assert with_preview, f"No voices have preview_url: {data['voices'][:2]}"

    def test_voice_select_and_persist(self, client):
        r = client.get(f"{BASE_URL}/api/voice/list", timeout=30)
        voices = r.json()["voices"]
        assert voices
        target = voices[0]["voice_id"]
        r2 = client.post(f"{BASE_URL}/api/voice/select", json={"voice_id": target}, timeout=15)
        assert r2.status_code == 200, r2.text
        assert r2.json()["current"] == target
        r3 = client.get(f"{BASE_URL}/api/voice/list", timeout=15)
        assert r3.json()["current"] == target

    def test_voice_speak_returns_audio(self, client):
        r = client.post(f"{BASE_URL}/api/voice/speak", json={"text": "Hello darling"}, timeout=60)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("audio_base64")
        # basic sanity: base64 decodes to some bytes
        raw = base64.b64decode(data["audio_base64"])
        assert len(raw) > 500


# ---------- Chat ----------
class TestChat:
    def test_chat_greeting(self, client):
        r = client.post(
            f"{BASE_URL}/api/chat",
            json={"message": "Hi Lilith, say hello briefly.", "session_id": "test-sess"},
            timeout=90,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "response" in data
        assert isinstance(data["response"], str) and len(data["response"].strip()) > 0


# ---------- Image ----------
class TestImage:
    def test_lilith_image_generation(self, client):
        r = client.post(
            f"{BASE_URL}/api/image/lilith",
            json={"outfit": "black_lace_lingerie"},
            timeout=180,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        url = data.get("url")
        assert url, data
        # Follow url - relative to BASE_URL if it starts with /
        full = url if url.startswith("http") else f"{BASE_URL}{url}"
        img = requests.get(full, timeout=60)
        assert img.status_code == 200
        assert len(img.content) > 5000, f"image too small: {len(img.content)} bytes"



# ---------- Status: face_swap + pose_controlnet ----------
class TestStatusBoosts:
    def test_status_includes_boost_engines(self, client):
        r = client.get(f"{BASE_URL}/api/status", timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "face_swap" in data, data.keys()
        assert "pose_controlnet" in data, data.keys()
        fs = data["face_swap"]
        pc = data["pose_controlnet"]
        # Just verify space names are referenced somewhere in status blob
        fs_blob = str(fs).lower()
        pc_blob = str(pc).lower()
        assert "felixrosberg" in fs_blob or "face-swap" in fs_blob or "face_swap" in fs_blob, fs
        assert "openpose" in pc_blob or "sjtu" in pc_blob, pc


# ---------- Presets ----------
class TestPresets:
    def test_presets_list_seeded(self, client):
        r = client.get(f"{BASE_URL}/api/presets", timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["count"] >= 8, f"expected >=8 starter presets, got {d['count']}"
        # Validate schema of first preset
        p = d["presets"][0]
        for key in ("id", "name", "outfit", "scene", "pose", "favorite_scenes"):
            assert key in p, f"missing key {key} in {p}"

    def test_preset_create_apply_delete(self, client):
        # Create
        payload = {
            "name": "TEST_look",
            "outfit": "red_silk_negligee",
            "scene": "rooftop_pool",
            "pose": "wine_pose",
            "seed": 12345,
        }
        r = client.post(f"{BASE_URL}/api/presets", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        created = r.json()
        assert created["name"] == "TEST_look"
        assert created["outfit"] == "red_silk_negligee"
        assert created["seed"] == 12345
        pid = created["id"]

        # List should include it
        r2 = client.get(f"{BASE_URL}/api/presets", timeout=30)
        ids = [p["id"] for p in r2.json()["presets"]]
        assert pid in ids

        # Apply
        r3 = client.post(f"{BASE_URL}/api/presets/{pid}/apply", timeout=30)
        assert r3.status_code == 200, r3.text
        applied = r3.json()
        assert applied.get("success") is True
        assert "apply" in applied
        ap = applied["apply"]
        assert ap["outfit"] == "red_silk_negligee"
        assert ap["scene"] == "rooftop_pool"
        assert ap["pose"] == "wine_pose"
        assert ap["seed"] == 12345
        assert "reference_strength" in ap

        # Delete
        r4 = client.delete(f"{BASE_URL}/api/presets/{pid}", timeout=30)
        assert r4.status_code == 200, r4.text

        # Thumbnail GET should 404 now
        r5 = client.get(f"{BASE_URL}/api/presets/{pid}/thumbnail", timeout=30)
        assert r5.status_code == 404

        # Apply on deleted returns 404
        r6 = client.post(f"{BASE_URL}/api/presets/{pid}/apply", timeout=30)
        assert r6.status_code == 404

    def test_preset_apply_with_voice_id_persists(self, client):
        # Grab a valid voice id
        vr = client.get(f"{BASE_URL}/api/voice/list", timeout=30).json()
        assert vr["voices"]
        target_voice = vr["voices"][-1]["voice_id"]
        # Save current voice to restore later
        original_voice = vr["current"]

        # Create preset with voice
        r = client.post(f"{BASE_URL}/api/presets", json={
            "name": "TEST_voice_look",
            "voice_id": target_voice,
        }, timeout=30)
        assert r.status_code == 200, r.text
        pid = r.json()["id"]
        try:
            r2 = client.post(f"{BASE_URL}/api/presets/{pid}/apply", timeout=30)
            assert r2.status_code == 200
            # Verify current voice updated
            cur = client.get(f"{BASE_URL}/api/voice/list", timeout=30).json()["current"]
            assert cur == target_voice, f"expected {target_voice} got {cur}"
        finally:
            client.delete(f"{BASE_URL}/api/presets/{pid}", timeout=30)
            # Restore
            if original_voice:
                client.post(f"{BASE_URL}/api/voice/select", json={"voice_id": original_voice}, timeout=15)


# ---------- Boost toggles (skip path when no reference set) ----------
class TestBoostToggles:
    def test_face_swap_skipped_without_reference(self, client):
        # Ensure no active face reference
        client.delete(f"{BASE_URL}/api/reference", timeout=15)
        r = client.post(f"{BASE_URL}/api/image/lilith", json={
            "outfit": "silk_robe",
            "use_face_swap": True,
        }, timeout=180)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("used_face_swap") is False, d

    def test_pose_controlnet_skipped_without_reference(self, client):
        client.delete(f"{BASE_URL}/api/pose_reference", timeout=15)
        r = client.post(f"{BASE_URL}/api/image/lilith", json={
            "outfit": "silk_robe",
            "use_pose_controlnet": True,
        }, timeout=180)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("used_pose_controlnet") is False, d

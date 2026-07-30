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

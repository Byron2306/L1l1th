import { useEffect, useRef, useState } from 'react';
import WardrobeDrawer from './WardrobeDrawer.jsx';
import GalleryDrawer from './GalleryDrawer.jsx';
import PresetsDrawer from './PresetsDrawer.jsx';

const BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND}/api`;

// ---------------------------------------------------------------------------
// Age gate — first-visit only, persisted in localStorage.
// ---------------------------------------------------------------------------

function AgeGate({ onEnter }) {
  return (
    <div className="gate-overlay" data-testid="age-gate">
      <div className="gate">
        <h1 className="serif">Lilith</h1>
        <div className="gate-rule" />
        <div className="gate-tag">Adults Only · 18 +</div>
        <p>
          This is a private, adult (18+) roleplay companion. Content is <em>suggestive and flirty</em>,
          intended for a mature audience. By entering you confirm you are of legal adult age
          in your jurisdiction and consent to adult-themed conversation and imagery.
        </p>
        <div className="gate-buttons">
          <button className="btn primary" onClick={onEnter} data-testid="age-gate-enter">
            I am 18 or older — enter
          </button>
        </div>
        <div className="fine">If you are under 18, please close this window.</div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Avatar side
// ---------------------------------------------------------------------------

function AvatarSide({
  imageUrl,
  imageLoading,
  speaking,
  audioLevel = 0,
  provider,
  currentSeed,
  onOpenWardrobe,
  onOpenGallery,
  onOpenPresets,
}) {
  // Scale up to ~1.03 at peak amplitude; brightness up to 1.15
  const scale = 1 + audioLevel * 0.03;
  const brightness = 1 + audioLevel * 0.15;
  const glow = 30 + audioLevel * 90;
  const frameStyle = speaking
    ? {
        transform: `scale(${scale})`,
        filter: `brightness(${brightness})`,
        boxShadow: `0 0 ${glow}px -5px rgba(198, 127, 138, ${0.4 + audioLevel * 0.5})`,
      }
    : undefined;
  return (
    <section className="avatar-side" data-testid="avatar-side">
      <div
        className={`avatar-frame ${speaking ? 'speaking' : ''}`}
        style={frameStyle}
        data-testid="avatar-frame"
      >
        <span className="gold-corner tl" />
        <span className="gold-corner tr" />
        <span className="gold-corner bl" />
        <span className="gold-corner br" />

        {imageUrl ? (
          <img src={imageUrl} alt="Lilith" className="avatar-img" data-testid="avatar-img" />
        ) : (
          <div className="avatar-empty">
            No portrait yet — open the wardrobe below to bring me to life.
          </div>
        )}

        {imageLoading && (
          <div className="avatar-loading" data-testid="avatar-loading">
            <span className="spinner" />
            Painting…
          </div>
        )}
      </div>

      <div className="name-plate">
        <div className="name serif">LILITH</div>
        <div className="rule" />
        <div className="tag">Adult Companion · 18+</div>
      </div>

      <div className="chip-row">
        {provider && (
          <div className="provider-chip" data-testid="provider-chip" title={provider}>
            {provider.length > 42 ? provider.slice(0, 40) + '…' : provider}
          </div>
        )}
        {currentSeed != null && (
          <div className="provider-chip gold-chip" data-testid="seed-chip" title="Current locked seed">
            seed · {currentSeed}
          </div>
        )}
      </div>

      <div className="avatar-actions">
        <button className="btn primary" onClick={onOpenWardrobe} data-testid="open-wardrobe-btn">
          Wardrobe
        </button>
        <button className="btn" onClick={onOpenPresets} data-testid="open-presets-btn">
          Presets
        </button>
        <button className="btn" onClick={onOpenGallery} data-testid="open-gallery-btn">
          Gallery
        </button>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Chat side
// ---------------------------------------------------------------------------

function ChatSide({ messages, onSend, busy, voiceOn, onToggleVoice, onClear, voices, voiceId, onSelectVoice, onPreviewVoice }) {
  const [text, setText] = useState('');
  const listRef = useRef(null);
  const [previewing, setPreviewing] = useState(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, busy]);

  const submit = () => {
    const t = text.trim();
    if (!t || busy) return;
    onSend(t);
    setText('');
  };

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const previewCurrent = () => {
    if (!voiceId) return;
    const v = voices.find((x) => x.voice_id === voiceId);
    if (v?.preview_url) {
      setPreviewing(voiceId);
      onPreviewVoice(v.preview_url).finally(() => setPreviewing(null));
    }
  };

  return (
    <section className="chat-side" data-testid="chat-side">
      <div className="chat-header">
        <div>
          <h2 className="serif">Conversation</h2>
          <div className="subtitle">A private evening</div>
        </div>
        <div className="header-actions">
          <button className="btn ghost" onClick={onClear} disabled={busy} data-testid="clear-history-btn">
            Clear
          </button>
        </div>
      </div>

      <div className="messages" ref={listRef} data-testid="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`} data-testid={`msg-${m.role}-${i}`}>
            {m.text && <div>{m.text}</div>}
            {m.imageUrl && (
              <img src={m.imageUrl} alt="generated" className="msg-img" data-testid={`msg-img-${i}`} />
            )}
            {m.meta && <div className="msg-meta">{m.meta}</div>}
          </div>
        ))}

        {busy && (
          <div className="typing" data-testid="typing-indicator">
            <span /><span /><span />
          </div>
        )}
      </div>

      <div className="composer">
        <div className="composer-row">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKey}
            placeholder="Say something to Lilith…"
            data-testid="chat-input"
            disabled={busy}
          />
          <button className="btn primary" onClick={submit} disabled={busy || !text.trim()} data-testid="send-btn">
            Send
          </button>
        </div>
        <div className="composer-controls">
          <button
            className={`toggle ${voiceOn ? 'on' : ''}`}
            onClick={onToggleVoice}
            data-testid="voice-toggle"
          >
            <span className="dot" />
            Voice {voiceOn ? 'On' : 'Off'}
          </button>
          {voiceOn && voices && voices.length > 0 && (
            <>
              <select
                className="voice-select"
                value={voiceId || ''}
                onChange={(e) => onSelectVoice(e.target.value)}
                data-testid="voice-select"
                disabled={busy}
                title="Voice"
              >
                {voices.map((v) => (
                  <option key={v.voice_id} value={v.voice_id}>
                    {v.name}
                  </option>
                ))}
              </select>
              <button
                className="btn ghost voice-preview-btn"
                onClick={previewCurrent}
                disabled={busy || !voiceId}
                title="Play a sample of this voice"
                data-testid="voice-preview-btn"
              >
                {previewing === voiceId ? '■' : '▶'}
              </button>
            </>
          )}
          <span className="dim" style={{ marginLeft: 'auto', fontSize: 11, letterSpacing: '0.06em' }}>
            Press Enter to send · Shift+Enter for a new line
          </span>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// App shell
// ---------------------------------------------------------------------------

export default function App() {
  const [gateOk, setGateOk] = useState(false);
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [voiceOn, setVoiceOn] = useState(true);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [presetsOpen, setPresetsOpen] = useState(false);
  const [galleryRefresh, setGalleryRefresh] = useState(0);
  const [presetsRefresh, setPresetsRefresh] = useState(0);

  // Fidelity boosts (Face-Swap + Pose ControlNet)
  const [useFaceSwap, setUseFaceSwap] = useState(false);
  const [usePoseControlnet, setUsePoseControlnet] = useState(false);
  const [userTouchedFaceSwap, setUserTouchedFaceSwap] = useState(false);

  // Last generation context (used to save current setup as a preset)
  const [lastContext, setLastContext] = useState({
    outfit: null, custom_prompt: null, scene: null, pose: null, galleryId: null,
  });

  const [avatarUrl, setAvatarUrl] = useState(null);
  const [avatarBusy, setAvatarBusy] = useState(false);
  const [chatProvider, setChatProvider] = useState(null);
  const [imageProvider, setImageProvider] = useState(null);
  const [speaking, setSpeaking] = useState(false);

  const [seedLocked, setSeedLocked] = useState(false);
  const [currentSeed, setCurrentSeed] = useState(null); // int or null
  const [reference, setReference] = useState(null);
  const [poseReference, setPoseReference] = useState(null);

  // Voice picker
  const [voices, setVoices] = useState([]);
  const [voiceId, setVoiceId] = useState(null);
  const [showVoicePicker, setShowVoicePicker] = useState(false);

  // Talking-avatar audio reactivity
  const [audioLevel, setAudioLevel] = useState(0);
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const sourceRef = useRef(null);
  const rafRef = useRef(null);

  const audioRef = useRef(null);

  useEffect(() => {
    if (localStorage.getItem('lilith:18ok') === 'yes') setGateOk(true);
    const savedLock = localStorage.getItem('lilith:seedLocked') === 'yes';
    const savedSeed = parseInt(localStorage.getItem('lilith:seed') || '', 10);
    if (savedLock && Number.isFinite(savedSeed)) {
      setSeedLocked(true);
      setCurrentSeed(savedSeed);
    }
    // Load current reference from backend
    fetch(`${API}/reference`).then((r) => r.json()).then((d) => {
      setReference(d.active ? d : null);
    }).catch(() => {});
    fetch(`${API}/pose_reference`).then((r) => r.json()).then((d) => {
      setPoseReference(d.active ? d : null);
    }).catch(() => {});
    // Load voice list + current
    fetch(`${API}/voice/list`).then((r) => r.json()).then((d) => {
      setVoices(d.voices || []);
      setVoiceId(d.current || null);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!gateOk) return;
    setMessages([
      {
        role: 'lilith',
        text: "Mmm, hello darling. I've been waiting for you… come sit with me. What would you like to talk about tonight?",
      },
    ]);
  }, [gateOk]);

  useEffect(() => {
    localStorage.setItem('lilith:seedLocked', seedLocked ? 'yes' : 'no');
    if (currentSeed != null) localStorage.setItem('lilith:seed', String(currentSeed));
  }, [seedLocked, currentSeed]);

  // Auto face-swap: when a face reference becomes active, default the boost
  // ON so her face stays consistent across outfits. Only auto-flip if the
  // user hasn't manually overridden the toggle.
  useEffect(() => {
    if (userTouchedFaceSwap) return;
    setUseFaceSwap(!!reference?.active);
  }, [reference?.active, userTouchedFaceSwap]);

  const enterSite = () => {
    localStorage.setItem('lilith:18ok', 'yes');
    setGateOk(true);
  };

  const _stopAudioAnalysis = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    setAudioLevel(0);
  };

  const _startAudioAnalysis = () => {
    const el = audioRef.current;
    if (!el) return;
    try {
      if (!audioCtxRef.current) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return;
        audioCtxRef.current = new Ctx();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') ctx.resume().catch(() => {});
      if (!sourceRef.current) {
        // MediaElementSource can only be created ONCE per element
        sourceRef.current = ctx.createMediaElementSource(el);
        analyserRef.current = ctx.createAnalyser();
        analyserRef.current.fftSize = 256;
        analyserRef.current.smoothingTimeConstant = 0.6;
        sourceRef.current.connect(analyserRef.current);
        analyserRef.current.connect(ctx.destination);
      }
      const analyser = analyserRef.current;
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteFrequencyData(data);
        // Emphasize the mid range (voice band ~200-2000Hz)
        let sum = 0, count = 0;
        for (let i = 4; i < 40; i++) { sum += data[i]; count++; }
        const avg = sum / count / 255; // 0..1
        setAudioLevel(avg);
        rafRef.current = requestAnimationFrame(tick);
      };
      tick();
    } catch (e) {
      // Audio graph failed — fail silently, playback still works
      console.warn('audio analysis failed', e);
    }
  };

  const playAudio = (b64) => {
    return new Promise((resolve) => {
      try {
        const el = audioRef.current;
        if (!el) return resolve();
        el.src = `data:audio/mp3;base64,${b64}`;
        setSpeaking(true);
        const onEnd = () => {
          setSpeaking(false);
          _stopAudioAnalysis();
          el.onended = null;
          el.onpause = null;
          resolve();
        };
        el.onended = onEnd;
        el.onpause = onEnd;
        el.play().then(() => _startAudioAnalysis()).catch(() => {
          setSpeaking(false);
          _stopAudioAnalysis();
          resolve();
        });
      } catch {
        setSpeaking(false);
        _stopAudioAnalysis();
        resolve();
      }
    });
  };

  // Fetch TTS for a sentence and return a resolver that starts playback.
  // We fetch and play sequentially so sentences never overlap, but we
  // pre-fetch the next while the current is playing.
  const fetchTTS = async (sentence) => {
    try {
      const r = await fetch(`${API}/voice/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: sentence, voice_id: voiceId || undefined }),
      });
      if (!r.ok) return null;
      const d = await r.json();
      return d.audio_base64 || null;
    } catch { return null; }
  };

  const previewVoice = (url) => {
    return new Promise((resolve) => {
      try {
        const el = audioRef.current;
        if (!el || !url) return resolve();
        el.src = url;
        // Preview URLs are on ElevenLabs' CDN (cross-origin, no CORS headers)
        // — WebAudio analyser can't read them, so we skip _startAudioAnalysis()
        // for previews and let the audio play plainly.
        const onEnd = () => {
          el.onended = null;
          el.onpause = null;
          resolve();
        };
        el.onended = onEnd;
        el.onpause = onEnd;
        el.play().catch(() => resolve());
      } catch {
        resolve();
      }
    });
  };

  const streamAbortRef = useRef(null);

  const sendMessage = async (text) => {
    // Cancel any prior in-flight stream so double-sends don't interleave chunks.
    if (streamAbortRef.current) {
      try { streamAbortRef.current.abort(); } catch { /* noop */ }
    }
    const abort = new AbortController();
    streamAbortRef.current = abort;

    setMessages((m) => [...m, { role: 'user', text }, { role: 'lilith', text: '', meta: null }]);
    setBusy(true);

    // Sentence pipeline state (voice-per-sentence, played in order)
    let carry = '';                // uncommitted text since the last sentence boundary
    let firstSentenceSent = false; // once true, we drop the min-length gate so terse
                                   // second/third sentences pipeline immediately
    let voiceChain = Promise.resolve();  // sequential playback queue
    const pumpSentence = (sentence) => {
      if (!voiceOn || !sentence.trim()) return;
      const ttsPromise = fetchTTS(sentence.trim());
      voiceChain = voiceChain.then(async () => {
        const b64 = await ttsPromise;
        if (b64) await playAudio(b64);
      });
    };
    const flushOnBoundary = () => {
      // Emit any complete sentence(s) in `carry`. Boundaries: . ? ! or newline
      // followed by whitespace/end. Require 12+ chars for the FIRST sentence
      // (helps skip abbreviations like "Mr." mid-name), then drop the gate.
      while (true) {
        const minLen = firstSentenceSent ? 1 : 12;
        const re = new RegExp(`^(.{${minLen},}?[.!?…]+["'”’)]*)(\\s+|$)`);
        const m = carry.match(re);
        if (!m) break;
        const sentence = m[1];
        pumpSentence(sentence);
        firstSentenceSent = true;
        carry = carry.slice(m[0].length);
      }
    };

    const appendChunk = (chunk) => {
      carry += chunk;
      setMessages((m) => {
        const copy = m.slice();
        const last = copy[copy.length - 1];
        if (last && last.role === 'lilith') {
          copy[copy.length - 1] = { ...last, text: (last.text || '') + chunk };
        }
        return copy;
      });
      flushOnBoundary();
    };

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
        signal: abort.signal,
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';
      let provider = null;

      // Parse SSE frames incrementally
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });

        let idx;
        while ((idx = buf.indexOf('\n\n')) !== -1) {
          const frame = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          const lines = frame.split('\n');
          let event = 'message';
          let dataStr = '';
          for (const line of lines) {
            if (line.startsWith('event:')) event = line.slice(6).trim();
            else if (line.startsWith('data:')) dataStr += line.slice(5).trim();
          }
          if (!dataStr) continue;
          let payload;
          try { payload = JSON.parse(dataStr); } catch { continue; }
          if (event === 'chunk' && typeof payload.text === 'string') {
            appendChunk(payload.text);
          } else if (event === 'done') {
            provider = payload.provider || null;
          } else if (event === 'error') {
            appendChunk('(the line went quiet…)');
          }
        }
      }

      // Flush trailing text as a final sentence (no terminator required)
      if (carry.trim()) {
        pumpSentence(carry);
        carry = '';
      }
      if (provider) {
        setChatProvider(provider);
        setMessages((m) => {
          const copy = m.slice();
          const last = copy[copy.length - 1];
          if (last && last.role === 'lilith') {
            copy[copy.length - 1] = { ...last, meta: `via ${provider}` };
          }
          return copy;
        });
      }
    } catch (err) {
      // Aborted streams (double-send cancel) drop silently — the newer send
      // will populate the bubble.
      if (err && err.name === 'AbortError') return;
      setMessages((m) => {
        // If we haven't received any text yet, mutate the empty bubble;
        // otherwise append a new error bubble.
        const copy = m.slice();
        const last = copy[copy.length - 1];
        if (last && last.role === 'lilith' && !last.text) {
          copy[copy.length - 1] = {
            role: 'lilith',
            text: '(the line went quiet for a moment…)',
            meta: 'connection error',
          };
          return copy;
        }
        return [...m, { role: 'lilith', text: '(the line went quiet for a moment…)', meta: 'connection error' }];
      });
    } finally {
      if (streamAbortRef.current === abort) streamAbortRef.current = null;
      setBusy(false);
    }
  };

  const clearHistory = async () => {
    setMessages([{ role: 'lilith', text: 'A fresh start, darling. Where were we? 💋' }]);
    try {
      await fetch(`${API}/clear`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}',
      });
    } catch {}
  };

  /**
   * Generate a portrait. `payload` is one of:
   *   { outfit: 'micro_bikini_beach', scene?, pose? }
   *   { outfit: 'random', scene?, pose? }
   *   { custom_prompt: 'gold silk gown, opera house…', scene?, pose? }
   */
  const generatePortrait = async (payload) => {
    setAvatarBusy(true);
    setDrawerOpen(false);
    try {
      const body = { ...payload };
      if (seedLocked && currentSeed != null) body.seed = currentSeed;
      const res = await fetch(`${API}/image/lilith`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      const url = `${BACKEND}${data.url}`;
      if (!seedLocked && data.seed != null) {
        setCurrentSeed(data.seed);
        // Auto-lock the seed after the first successful gen so style stays
        // consistent across follow-up outfits/scenes (item e — style drift).
        setSeedLocked(true);
      }
      setImageProvider(data.provider || null);
      setAvatarUrl(url);
      setLastContext({
        outfit: payload.custom_prompt ? null : (payload.outfit || null),
        custom_prompt: payload.custom_prompt || null,
        scene: payload.scene || null,
        pose: payload.pose || null,
        galleryId: data.gallery_id || null,
      });
      const bits = [
        payload.custom_prompt ? 'custom' : (payload.outfit || 'random'),
      ];
      if (payload.scene) bits.push(payload.scene);
      if (payload.pose) bits.push(payload.pose);
      if (data.used_reference) bits.push('ref');
      if (data.used_pose_controlnet) bits.push('pose-ctrl');
      if (data.used_face_swap) bits.push('face-swap');
      if (data.used_enhance) bits.push('2x');
      bits.push(`seed ${data.seed}`);
      bits.push(data.provider);
      setMessages((m) => [
        ...m,
        {
          role: 'lilith',
          text: 'How do I look, darling? 💋',
          imageUrl: url,
          meta: bits.filter(Boolean).join(' · '),
        },
      ]);
      setGalleryRefresh((k) => k + 1);
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'lilith', text: '(the paint smudged — try again in a moment, darling)', meta: 'image error' },
      ]);
    } finally {
      setAvatarBusy(false);
    }
  };

  // --- Reference management -------------------------------------------------

  const setReferenceFromGallery = async (entry) => {
    try {
      const r = await fetch(`${API}/reference/gallery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gallery_id: entry.id, strength: 0.32 }),
      });
      const d = await r.json();
      if (d.active) setReference(d);
    } catch {}
  };

  const uploadReference = async (file) => {
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await fetch(`${API}/reference/upload`, { method: 'POST', body: fd });
      const d = await r.json();
      if (d.active) setReference(d);
    } catch {}
  };

  const clearReference = async () => {
    try { await fetch(`${API}/reference`, { method: 'DELETE' }); } catch {}
    setReference(null);
  };

  const setReferenceStrength = async (strength) => {
    try {
      const r = await fetch(`${API}/reference/strength`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strength }),
      });
      const d = await r.json();
      if (d.active) setReference(d);
    } catch {}
  };

  // Pose reference
  const uploadPoseReference = async (file) => {
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await fetch(`${API}/pose_reference/upload`, { method: 'POST', body: fd });
      const d = await r.json();
      if (d.active) setPoseReference(d);
    } catch {}
  };
  const clearPoseReference = async () => {
    try { await fetch(`${API}/pose_reference`, { method: 'DELETE' }); } catch {}
    setPoseReference(null);
  };

  const galleryDelete = async (id) => {
    try { await fetch(`${API}/gallery/${id}`, { method: 'DELETE' }); }
    catch {}
    // if the deleted entry is currently displayed, clear the avatar
    if (avatarUrl && avatarUrl.endsWith(`/api/gallery/${id}`)) setAvatarUrl(null);
  };

  const galleryPick = (entry) => {
    setAvatarUrl(`${BACKEND}${entry.url}`);
    // Adopt this entry's seed so subsequent generations keep the same face
    if (entry.seed != null) {
      setCurrentSeed(entry.seed);
      setSeedLocked(true);
    }
    setGalleryOpen(false);
    setMessages((m) => [
      ...m,
      {
        role: 'lilith',
        text: 'Bringing back that look for you~ 💋',
        imageUrl: `${BACKEND}${entry.url}`,
        meta: `${entry.label} · seed ${entry.seed ?? '—'}`,
      },
    ]);
  };

  const selectVoice = async (id) => {
    setVoiceId(id);
    try {
      await fetch(`${API}/voice/select`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: id }),
      });
    } catch {}
  };

  const applyPreset = async (result) => {
    const apply = result?.apply || {};
    // Sync UI state
    if (apply.voice_id) setVoiceId(apply.voice_id);
    if (typeof apply.seed === 'number') {
      setCurrentSeed(apply.seed);
      setSeedLocked(true);
    }
    // Refresh live references (backend already updated them)
    try {
      const [rf, rp] = await Promise.all([
        fetch(`${API}/reference`).then((r) => r.json()),
        fetch(`${API}/pose_reference`).then((r) => r.json()),
      ]);
      setReference(rf.active ? rf : null);
      setPoseReference(rp.active ? rp : null);
    } catch {}
    setPresetsOpen(false);
    // Immediately generate a fresh portrait with this preset
    const payload = {};
    if (apply.custom_prompt) payload.custom_prompt = apply.custom_prompt;
    else if (apply.outfit) payload.outfit = apply.outfit;
    else payload.outfit = 'random';
    if (apply.scene) payload.scene = apply.scene;
    if (apply.pose) payload.pose = apply.pose;
    payload.use_face_swap = useFaceSwap;
    payload.use_pose_controlnet = usePoseControlnet;
    generatePortrait(payload);
  };

  if (!gateOk) return <AgeGate onEnter={enterSite} />;

  return (
    <>
      <div className="app" data-testid="app">
        <AvatarSide
          imageUrl={avatarUrl}
          imageLoading={avatarBusy}
          speaking={speaking}
          audioLevel={audioLevel}
          provider={imageProvider || chatProvider}
          currentSeed={seedLocked ? currentSeed : null}
          onOpenWardrobe={() => setDrawerOpen(true)}
          onOpenGallery={() => setGalleryOpen(true)}
          onOpenPresets={() => { setPresetsRefresh((k) => k + 1); setPresetsOpen(true); }}
        />
        <ChatSide
          messages={messages}
          onSend={sendMessage}
          busy={busy}
          voiceOn={voiceOn}
          onToggleVoice={() => setVoiceOn((v) => !v)}
          onClear={clearHistory}
          voices={voices}
          voiceId={voiceId}
          onSelectVoice={selectVoice}
          onPreviewVoice={previewVoice}
        />
      </div>

      <WardrobeDrawer
        api={API}
        backend={BACKEND}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onPick={generatePortrait}
        busy={avatarBusy}
        seedLocked={seedLocked}
        currentSeed={currentSeed}
        onToggleSeedLock={() => setSeedLocked((v) => !v)}
        onSetSeed={(n) => setCurrentSeed(n)}
        reference={reference}
        onClearReference={clearReference}
        onSetReferenceStrength={setReferenceStrength}
        onUploadReference={uploadReference}
        poseReference={poseReference}
        onUploadPoseReference={uploadPoseReference}
        onClearPoseReference={clearPoseReference}
        useFaceSwap={useFaceSwap}
        onToggleFaceSwap={() => { setUserTouchedFaceSwap(true); setUseFaceSwap((v) => !v); }}
        usePoseControlnet={usePoseControlnet}
        onTogglePoseControlnet={() => setUsePoseControlnet((v) => !v)}
      />

      <PresetsDrawer
        api={API}
        backend={BACKEND}
        open={presetsOpen}
        onClose={() => setPresetsOpen(false)}
        onApply={applyPreset}
        currentOutfit={lastContext.outfit}
        currentCustomPrompt={lastContext.custom_prompt}
        currentScene={lastContext.scene}
        currentPose={lastContext.pose}
        currentSeed={seedLocked ? currentSeed : null}
        currentVoiceId={voiceId}
        currentReferenceStrength={reference?.strength ?? 0.32}
        lastGalleryId={lastContext.galleryId}
        refreshKey={presetsRefresh}
      />

      <GalleryDrawer
        api={API}
        open={galleryOpen}
        onClose={() => setGalleryOpen(false)}
        onSelect={galleryPick}
        onDelete={galleryDelete}
        onSetReference={setReferenceFromGallery}
        activeReferenceId={reference?.gallery_id || null}
        refreshKey={galleryRefresh}
      />

      <audio ref={audioRef} style={{ display: 'none' }} />
    </>
  );
}

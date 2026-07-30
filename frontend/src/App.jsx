import { useEffect, useRef, useState } from 'react';
import WardrobeDrawer from './WardrobeDrawer.jsx';
import GalleryDrawer from './GalleryDrawer.jsx';

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
  provider,
  currentSeed,
  onOpenWardrobe,
  onOpenGallery,
}) {
  return (
    <section className="avatar-side" data-testid="avatar-side">
      <div className={`avatar-frame ${speaking ? 'speaking' : ''}`} data-testid="avatar-frame">
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

function ChatSide({ messages, onSend, busy, voiceOn, onToggleVoice, onClear }) {
  const [text, setText] = useState('');
  const listRef = useRef(null);

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
  const [galleryRefresh, setGalleryRefresh] = useState(0);

  const [avatarUrl, setAvatarUrl] = useState(null);
  const [avatarBusy, setAvatarBusy] = useState(false);
  const [chatProvider, setChatProvider] = useState(null);
  const [imageProvider, setImageProvider] = useState(null);
  const [speaking, setSpeaking] = useState(false);

  const [seedLocked, setSeedLocked] = useState(false);
  const [currentSeed, setCurrentSeed] = useState(null); // int or null

  const audioRef = useRef(null);

  useEffect(() => {
    if (localStorage.getItem('lilith:18ok') === 'yes') setGateOk(true);
    const savedLock = localStorage.getItem('lilith:seedLocked') === 'yes';
    const savedSeed = parseInt(localStorage.getItem('lilith:seed') || '', 10);
    if (savedLock && Number.isFinite(savedSeed)) {
      setSeedLocked(true);
      setCurrentSeed(savedSeed);
    }
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

  const enterSite = () => {
    localStorage.setItem('lilith:18ok', 'yes');
    setGateOk(true);
  };

  const playAudio = (b64) => {
    try {
      const el = audioRef.current;
      if (!el) return;
      el.src = `data:audio/mp3;base64,${b64}`;
      setSpeaking(true);
      el.play().catch(() => setSpeaking(false));
      el.onended = () => setSpeaking(false);
    } catch { setSpeaking(false); }
  };

  const sendMessage = async (text) => {
    setMessages((m) => [...m, { role: 'user', text }]);
    setBusy(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      const reply = data.response || '…';
      setChatProvider(data.provider || null);
      setMessages((m) => [
        ...m,
        { role: 'lilith', text: reply, meta: data.provider ? `via ${data.provider}` : null },
      ]);

      if (voiceOn && reply) {
        try {
          const vr = await fetch(`${API}/voice/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: reply }),
          });
          if (vr.ok) {
            const vd = await vr.json();
            if (vd.audio_base64) playAudio(vd.audio_base64);
          }
        } catch { /* voice failure silent */ }
      }
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'lilith', text: '(the line went quiet for a moment…)', meta: 'connection error' },
      ]);
    } finally {
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
   *   { outfit: 'micro_bikini_beach' }
   *   { outfit: 'random' }
   *   { custom_prompt: 'gold silk gown, opera house…' }
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
      // If not seed-locked, still remember the seed that was used so the user can lock it later
      if (!seedLocked && data.seed != null) setCurrentSeed(data.seed);
      setImageProvider(data.provider || null);
      setAvatarUrl(url);
      setMessages((m) => [
        ...m,
        {
          role: 'lilith',
          text: 'How do I look, darling? 💋',
          imageUrl: url,
          meta: `${payload.custom_prompt ? 'custom' : 'outfit'} · seed ${data.seed} · ${data.provider}`,
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

  if (!gateOk) return <AgeGate onEnter={enterSite} />;

  return (
    <>
      <div className="app" data-testid="app">
        <AvatarSide
          imageUrl={avatarUrl}
          imageLoading={avatarBusy}
          speaking={speaking}
          provider={imageProvider || chatProvider}
          currentSeed={seedLocked ? currentSeed : null}
          onOpenWardrobe={() => setDrawerOpen(true)}
          onOpenGallery={() => setGalleryOpen(true)}
        />
        <ChatSide
          messages={messages}
          onSend={sendMessage}
          busy={busy}
          voiceOn={voiceOn}
          onToggleVoice={() => setVoiceOn((v) => !v)}
          onClear={clearHistory}
        />
      </div>

      <WardrobeDrawer
        api={API}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onPick={generatePortrait}
        busy={avatarBusy}
        seedLocked={seedLocked}
        currentSeed={currentSeed}
        onToggleSeedLock={() => setSeedLocked((v) => !v)}
        onSetSeed={(n) => setCurrentSeed(n)}
      />

      <GalleryDrawer
        api={API}
        open={galleryOpen}
        onClose={() => setGalleryOpen(false)}
        onSelect={galleryPick}
        onDelete={galleryDelete}
        refreshKey={galleryRefresh}
      />

      <audio ref={audioRef} style={{ display: 'none' }} />
    </>
  );
}

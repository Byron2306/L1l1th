import { useEffect, useMemo, useRef, useState } from 'react';

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
          <button
            className="btn primary"
            onClick={onEnter}
            data-testid="age-gate-enter"
          >
            I am 18 or older — enter
          </button>
        </div>
        <div className="fine">If you are under 18, please close this window.</div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Wardrobe drawer — pick an outfit, generate an image.
// ---------------------------------------------------------------------------

const CATEGORY_ORDER = ['lingerie', 'swimwear', 'boudoir', 'themed'];
const CATEGORY_LABELS = {
  lingerie: 'Lingerie',
  swimwear: 'Swimwear',
  boudoir: 'Boudoir',
  themed: 'Themed',
};

function WardrobeDrawer({ open, onClose, onPick, busy }) {
  const [outfits, setOutfits] = useState(null);

  useEffect(() => {
    if (!open || outfits) return;
    fetch(`${API}/image/outfits`)
      .then((r) => r.json())
      .then((d) => setOutfits(d.by_category || {}))
      .catch(() => setOutfits({}));
  }, [open, outfits]);

  if (!open) return null;

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} data-testid="wardrobe-backdrop" />
      <aside className="drawer" data-testid="wardrobe-drawer">
        <div className="drawer-close">
          <div>
            <h3 className="serif">Wardrobe</h3>
            <div className="subtitle">Choose a look</div>
          </div>
          <button className="btn ghost" onClick={onClose} data-testid="wardrobe-close">Close</button>
        </div>

        <button
          className="btn primary"
          style={{ width: '100%', marginBottom: 22 }}
          disabled={busy}
          onClick={() => onPick('random')}
          data-testid="wardrobe-surprise"
        >
          {busy ? 'Painting…' : 'Surprise Me'}
        </button>

        {!outfits && <div className="dim serif italic">Loading wardrobe…</div>}

        {outfits &&
          CATEGORY_ORDER.filter((c) => outfits[c]?.length).map((cat) => (
            <div key={cat} className="category">
              <div className="cat-label">{CATEGORY_LABELS[cat] || cat}</div>
              <div className="outfit-grid">
                {outfits[cat].map((o) => (
                  <button
                    key={o.id}
                    className="outfit"
                    disabled={busy}
                    onClick={() => onPick(o.id)}
                    data-testid={`outfit-${o.id}`}
                  >
                    {o.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
      </aside>
    </>
  );
}

// ---------------------------------------------------------------------------
// Avatar side
// ---------------------------------------------------------------------------

function AvatarSide({ imageUrl, imageLoading, speaking, provider, onOpenWardrobe }) {
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

      {provider && (
        <div className="provider-chip" data-testid="provider-chip">
          {provider}
        </div>
      )}

      <div className="avatar-actions">
        <button
          className="btn primary"
          onClick={onOpenWardrobe}
          data-testid="open-wardrobe-btn"
        >
          Open Wardrobe
        </button>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Chat side
// ---------------------------------------------------------------------------

function ChatSide({
  messages,
  onSend,
  busy,
  voiceOn,
  onToggleVoice,
  onClear,
}) {
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
          <button
            className="btn ghost"
            onClick={onClear}
            disabled={busy}
            data-testid="clear-history-btn"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="messages" ref={listRef} data-testid="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`} data-testid={`msg-${m.role}-${i}`}>
            {m.text && <div>{m.text}</div>}
            {m.imageUrl && (
              <img
                src={m.imageUrl}
                alt="generated"
                className="msg-img"
                data-testid={`msg-img-${i}`}
              />
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
          <button
            className="btn primary"
            onClick={submit}
            disabled={busy || !text.trim()}
            data-testid="send-btn"
          >
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
  const [avatarUrl, setAvatarUrl] = useState(null);
  const [avatarBusy, setAvatarBusy] = useState(false);
  const [chatProvider, setChatProvider] = useState(null);
  const [speaking, setSpeaking] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    if (localStorage.getItem('lilith:18ok') === 'yes') setGateOk(true);
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
    } catch {
      setSpeaking(false);
    }
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
        } catch { /* voice failure is silent */ }
      }
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: 'lilith', text: '(the line went quiet for a moment…)', meta: 'connection error' },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const clearHistory = async () => {
    setMessages([
      {
        role: 'lilith',
        text: 'A fresh start, darling. Where were we? 💋',
      },
    ]);
    try { await fetch(`${API}/clear`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}' }); } catch {}
  };

  const pickOutfit = async (outfitId) => {
    setAvatarBusy(true);
    setDrawerOpen(false);
    try {
      // Use direct URL so browser can render the returned image (webp/png)
      const url = `${API}/image/lilith?outfit=${encodeURIComponent(outfitId)}&t=${Date.now()}`;
      // Preload — this way we swap in only once the new image is ready
      const img = new Image();
      img.onload = () => {
        setAvatarUrl(url);
        setAvatarBusy(false);
        setMessages((m) => [
          ...m,
          { role: 'lilith', text: 'How do I look, darling? 💋', imageUrl: url, meta: `outfit · ${outfitId}` },
        ]);
      };
      img.onerror = () => setAvatarBusy(false);
      img.src = url;
    } catch {
      setAvatarBusy(false);
    }
  };

  if (!gateOk) return <AgeGate onEnter={enterSite} />;

  return (
    <>
      <div className="app" data-testid="app">
        <AvatarSide
          imageUrl={avatarUrl}
          imageLoading={avatarBusy}
          speaking={speaking}
          provider={chatProvider}
          onOpenWardrobe={() => setDrawerOpen(true)}
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
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onPick={pickOutfit}
        busy={avatarBusy}
      />

      <audio ref={audioRef} style={{ display: 'none' }} />
    </>
  );
}

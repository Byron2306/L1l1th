import { useEffect, useState } from 'react';

const CATEGORY_ORDER = ['lingerie', 'swimwear', 'boudoir', 'themed'];
const CATEGORY_LABELS = {
  lingerie: 'Lingerie',
  swimwear: 'Swimwear',
  boudoir: 'Boudoir',
  themed: 'Themed',
};

/**
 * Wardrobe drawer
 * - Seed lock (pin/unpin) + numeric input
 * - Custom outfit textarea (free-form)
 * - Categorized outfit picker (from /api/image/outfits)
 */
export default function WardrobeDrawer({
  api,
  open,
  onClose,
  onPick,        // (payload) => void  where payload = {outfit?} or {custom_prompt?}
  busy,
  seedLocked,
  currentSeed,
  onToggleSeedLock,
  onSetSeed,
}) {
  const [outfits, setOutfits] = useState(null);
  const [customText, setCustomText] = useState('');
  const [seedInput, setSeedInput] = useState('');

  useEffect(() => {
    if (!open || outfits) return;
    fetch(`${api}/image/outfits`)
      .then((r) => r.json())
      .then((d) => setOutfits(d.by_category || {}))
      .catch(() => setOutfits({}));
  }, [api, open, outfits]);

  useEffect(() => {
    setSeedInput(currentSeed != null ? String(currentSeed) : '');
  }, [currentSeed]);

  if (!open) return null;

  const submitCustom = () => {
    const t = customText.trim();
    if (!t || busy) return;
    onPick({ custom_prompt: t });
  };

  const commitSeed = () => {
    const n = parseInt(seedInput, 10);
    if (Number.isFinite(n) && n >= 0) onSetSeed(n);
  };

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

        {/* --- Seed lock --- */}
        <div className="seed-panel" data-testid="seed-panel">
          <div className="seed-row">
            <button
              className={`toggle ${seedLocked ? 'on' : ''}`}
              onClick={onToggleSeedLock}
              data-testid="seed-lock-toggle"
              title={seedLocked ? 'Locked — same face across looks' : 'Unlocked — random face each time'}
            >
              <span className="dot" />
              {seedLocked ? 'Face Locked' : 'Face Random'}
            </button>
            <input
              className="seed-input"
              value={seedInput}
              placeholder="seed"
              inputMode="numeric"
              onChange={(e) => setSeedInput(e.target.value.replace(/[^0-9]/g, '').slice(0, 10))}
              onBlur={commitSeed}
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); commitSeed(); e.target.blur(); } }}
              disabled={!seedLocked}
              data-testid="seed-input"
            />
          </div>
          <div className="seed-hint dim">
            {seedLocked
              ? 'Same seed keeps her face consistent across new outfits and scenes.'
              : 'Pin a seed to keep the same Lilith across looks.'}
          </div>
        </div>

        {/* --- Custom outfit --- */}
        <div className="custom-panel" data-testid="custom-panel">
          <div className="cat-label" style={{ marginBottom: 10 }}>Describe her look</div>
          <textarea
            className="custom-input"
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            placeholder="e.g. gold silk gown, opera house balcony, chandelier lighting…"
            rows={3}
            data-testid="custom-outfit-input"
          />
          <button
            className="btn primary"
            style={{ width: '100%', marginTop: 8 }}
            disabled={busy || !customText.trim()}
            onClick={submitCustom}
            data-testid="custom-outfit-submit"
          >
            {busy ? 'Painting…' : 'Wear This'}
          </button>
        </div>

        {/* --- Surprise --- */}
        <button
          className="btn"
          style={{ width: '100%', marginBottom: 22 }}
          disabled={busy}
          onClick={() => onPick({ outfit: 'random' })}
          data-testid="wardrobe-surprise"
        >
          Surprise Me
        </button>

        {/* --- Catalog --- */}
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
                    onClick={() => onPick({ outfit: o.id })}
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

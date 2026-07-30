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
 * - Reference face card (current ref preview + strength slider + clear + upload)
 * - Seed lock (pin/unpin) + numeric input
 * - Scene + Pose selects
 * - Custom outfit textarea (free-form)
 * - Surprise / Categorized outfit picker
 */
export default function WardrobeDrawer({
  api,
  backend,
  open,
  onClose,
  onPick,        // ({outfit?|custom_prompt?, scene?, pose?}) => void
  busy,
  seedLocked,
  currentSeed,
  onToggleSeedLock,
  onSetSeed,
  reference,               // face ref
  onClearReference,
  onSetReferenceStrength,
  onUploadReference,
  poseReference,           // pose ref
  onUploadPoseReference,
  onClearPoseReference,
}) {
  const [outfits, setOutfits] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [poses, setPoses] = useState([]);
  const [customText, setCustomText] = useState('');
  const [seedInput, setSeedInput] = useState('');
  const [scene, setScene] = useState('');
  const [pose, setPose] = useState('');

  useEffect(() => {
    if (!open) return;
    if (!outfits) {
      fetch(`${api}/image/outfits`).then((r) => r.json())
        .then((d) => setOutfits(d.by_category || {})).catch(() => setOutfits({}));
    }
    if (!scenes.length) {
      fetch(`${api}/image/scenes`).then((r) => r.json())
        .then((d) => setScenes(d.scenes || [])).catch(() => setScenes([]));
    }
    if (!poses.length) {
      fetch(`${api}/image/poses`).then((r) => r.json())
        .then((d) => setPoses(d.poses || [])).catch(() => setPoses([]));
    }
  }, [api, open]); // eslint-disable-line

  useEffect(() => {
    setSeedInput(currentSeed != null ? String(currentSeed) : '');
  }, [currentSeed]);

  if (!open) return null;

  const wrapPick = (extra) => onPick({ ...extra, scene: scene || null, pose: pose || null });
  const submitCustom = () => {
    const t = customText.trim();
    if (!t || busy) return;
    wrapPick({ custom_prompt: t });
  };
  const commitSeed = () => {
    const n = parseInt(seedInput, 10);
    if (Number.isFinite(n) && n >= 0) onSetSeed(n);
  };
  const onUploadChange = (e) => {
    const f = e.target.files?.[0];
    if (f) onUploadReference(f);
    e.target.value = '';
  };
  const onPoseUploadChange = (e) => {
    const f = e.target.files?.[0];
    if (f) onUploadPoseReference(f);
    e.target.value = '';
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

        {/* --- Reference face --- */}
        <div className="ref-panel" data-testid="ref-panel">
          <div className="cat-label" style={{ marginBottom: 10 }}>Face Reference</div>
          {reference?.active ? (
            <div className="ref-row">
              <img
                className="ref-thumb"
                src={`${backend}${reference.url}`}
                alt="reference"
                data-testid="ref-thumb"
              />
              <div className="ref-body">
                <div className="tiny gold">Active</div>
                <div className="dim serif italic" style={{ fontSize: 12, marginTop: 2 }}>
                  Every new look uses this as her face.
                </div>
                <div className="ref-strength">
                  <label className="tiny dim">Fidelity · {Math.round((1 - reference.strength) * 100)}%</label>
                  <input
                    type="range"
                    min="0.10" max="0.85" step="0.02"
                    value={reference.strength}
                    onChange={(e) => onSetReferenceStrength(parseFloat(e.target.value))}
                    className="ref-slider"
                    data-testid="ref-strength"
                  />
                </div>
                <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
                  <label className="btn ghost" style={{ cursor: 'pointer' }}>
                    Upload…
                    <input type="file" accept="image/*" hidden onChange={onUploadChange} data-testid="ref-upload" />
                  </label>
                  <button className="btn ghost" onClick={onClearReference} data-testid="ref-clear">Clear</button>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="dim serif italic" style={{ fontSize: 12.5, lineHeight: 1.5 }}>
                No reference yet. Star a gallery look, or upload your own.
              </div>
              <label className="btn ghost" style={{ display: 'inline-block', marginTop: 10, cursor: 'pointer' }}>
                Upload reference…
                <input type="file" accept="image/*" hidden onChange={onUploadChange} data-testid="ref-upload" />
              </label>
            </>
          )}
        </div>

        {/* --- Pose reference --- */}
        <div className="ref-panel" data-testid="pose-ref-panel">
          <div className="cat-label" style={{ marginBottom: 10 }}>Pose Reference</div>
          {poseReference?.active ? (
            <div className="ref-row">
              <img
                className="ref-thumb"
                src={`${backend}${poseReference.url}`}
                alt="pose reference"
                data-testid="pose-ref-thumb"
              />
              <div className="ref-body">
                <div className="tiny gold">Active</div>
                <div className="dim serif italic" style={{ fontSize: 12, marginTop: 2 }}>
                  Body pose will follow this photo.
                </div>
                <div className="dim" style={{ fontSize: 10, marginTop: 6, letterSpacing: '0.06em' }}>
                  Beta: pose is hinted via prompt. Full ControlNet OpenPose coming later.
                </div>
                <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
                  <label className="btn ghost" style={{ cursor: 'pointer' }}>
                    Replace…
                    <input type="file" accept="image/*" hidden onChange={onPoseUploadChange} data-testid="pose-ref-upload" />
                  </label>
                  <button className="btn ghost" onClick={onClearPoseReference} data-testid="pose-ref-clear">Clear</button>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="dim serif italic" style={{ fontSize: 12.5, lineHeight: 1.5 }}>
                Upload a photo whose body position you want her to mimic.
              </div>
              <label className="btn ghost" style={{ display: 'inline-block', marginTop: 10, cursor: 'pointer' }}>
                Upload pose…
                <input type="file" accept="image/*" hidden onChange={onPoseUploadChange} data-testid="pose-ref-upload" />
              </label>
            </>
          )}
        </div>

        {/* --- Seed lock --- */}
        <div className="seed-panel" data-testid="seed-panel">
          <div className="seed-row">
            <button
              className={`toggle ${seedLocked ? 'on' : ''}`}
              onClick={onToggleSeedLock}
              data-testid="seed-lock-toggle"
            >
              <span className="dot" />
              {seedLocked ? 'Seed Locked' : 'Seed Random'}
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
            Face reference is the primary anchor. Seed is a secondary nudge.
          </div>
        </div>

        {/* --- Scene + Pose --- */}
        <div className="axis-panel">
          <div className="axis-row">
            <label className="tiny dim">Scene</label>
            <select
              value={scene}
              onChange={(e) => setScene(e.target.value)}
              className="axis-select"
              data-testid="scene-select"
              disabled={busy}
            >
              <option value="">— none —</option>
              {scenes.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
            </select>
          </div>
          <div className="axis-row">
            <label className="tiny dim">Pose</label>
            <select
              value={pose}
              onChange={(e) => setPose(e.target.value)}
              className="axis-select"
              data-testid="pose-select"
              disabled={busy}
            >
              <option value="">— none —</option>
              {poses.map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
            </select>
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
          onClick={() => wrapPick({ outfit: 'random' })}
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
                    onClick={() => wrapPick({ outfit: o.id })}
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

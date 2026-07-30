import { useEffect, useState } from 'react';

/**
 * Presets drawer — one-tap "looks":
 *   name + outfit + scene + pose + seed + voice + snapshot of face/pose refs.
 * Tap a card to apply. Tap ✎ to save the current setup as a new preset.
 */
export default function PresetsDrawer({
  api,
  backend,
  open,
  onClose,
  onApply,           // (result) => void — server returns {apply: {...}} to hand to generatePortrait
  currentOutfit,     // string | null (outfit id or 'custom' or null)
  currentCustomPrompt,
  currentScene,
  currentPose,
  currentSeed,       // int | null
  currentVoiceId,    // string | null
  currentReferenceStrength,
  lastGalleryId,     // for thumbnail
  refreshKey,
}) {
  const [presets, setPresets] = useState(null);
  const [saving, setSaving] = useState(false);
  const [name, setName] = useState('');
  const [applyingId, setApplyingId] = useState(null);

  useEffect(() => {
    if (!open) return;
    setPresets(null);
    fetch(`${api}/presets`)
      .then((r) => r.json())
      .then((d) => setPresets(d.presets || []))
      .catch(() => setPresets([]));
  }, [api, open, refreshKey]);

  const save = async () => {
    if (!name.trim() || saving) return;
    setSaving(true);
    try {
      const payload = {
        name: name.trim(),
        outfit: (currentOutfit && currentOutfit !== 'custom') ? currentOutfit : null,
        custom_prompt: currentCustomPrompt || null,
        scene: currentScene || null,
        pose: currentPose || null,
        seed: (typeof currentSeed === 'number' && Number.isFinite(currentSeed)) ? currentSeed : null,
        voice_id: currentVoiceId || null,
        reference_strength: typeof currentReferenceStrength === 'number' ? currentReferenceStrength : 0.32,
        include_face_reference: true,
        include_pose_reference: true,
        thumbnail_gallery_id: lastGalleryId || null,
      };
      const r = await fetch(`${api}/presets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (r.ok) {
        const p = await r.json();
        setPresets((ps) => [p, ...(ps || [])]);
        setName('');
      }
    } catch { /* silent */ }
    finally { setSaving(false); }
  };

  const apply = async (preset) => {
    setApplyingId(preset.id);
    try {
      const r = await fetch(`${api}/presets/${preset.id}/apply`, { method: 'POST' });
      if (r.ok) {
        const d = await r.json();
        onApply(d);
      }
    } catch { /* silent */ }
    finally { setApplyingId(null); }
  };

  const del = async (id) => {
    if (!confirm('Delete this preset?')) return;
    try {
      await fetch(`${api}/presets/${id}`, { method: 'DELETE' });
      setPresets((ps) => (ps || []).filter((p) => p.id !== id));
    } catch { /* silent */ }
  };

  if (!open) return null;

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} data-testid="presets-backdrop" />
      <aside className="drawer presets-drawer" data-testid="presets-drawer">
        <div className="drawer-close">
          <div>
            <h3 className="serif">Presets</h3>
            <div className="subtitle">{presets ? `${presets.length} saved looks` : 'Loading…'}</div>
          </div>
          <button className="btn ghost" onClick={onClose} data-testid="presets-close">Close</button>
        </div>

        <div className="preset-save-row">
          <input
            className="preset-name-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name this look… e.g. Rooftop Date"
            maxLength={80}
            data-testid="preset-name-input"
          />
          <button
            className="btn primary"
            onClick={save}
            disabled={saving || !name.trim()}
            data-testid="preset-save-btn"
            title="Save current setup as a preset"
          >
            {saving ? 'Saving…' : 'Save current'}
          </button>
        </div>

        {presets && presets.length === 0 && (
          <div className="dim serif italic" style={{ padding: '40px 0', textAlign: 'center' }}>
            No presets yet. Save your current setup above.
          </div>
        )}

        <div className="preset-grid" data-testid="preset-grid">
          {(presets || []).map((p) => (
            <div key={p.id} className="preset-card" data-testid={`preset-card-${p.id}`}>
              <button
                className="preset-thumb"
                onClick={() => apply(p)}
                disabled={applyingId === p.id}
                title="Apply this preset"
                data-testid={`preset-apply-${p.id}`}
              >
                {p.thumbnail_url ? (
                  <img src={`${backend}${p.thumbnail_url}`} alt={p.name} loading="lazy" />
                ) : (
                  <div className="preset-thumb-empty serif">{p.name.slice(0, 1) || '·'}</div>
                )}
                {applyingId === p.id && <span className="preset-applying">Applying…</span>}
              </button>
              <div className="preset-meta">
                <div className="preset-name serif" title={p.name}>{p.name}</div>
                <div className="preset-tags">
                  {p.outfit && <span className="preset-tag">{p.outfit.replaceAll('_', ' ')}</span>}
                  {p.scene && <span className="preset-tag">{p.scene.replaceAll('_', ' ')}</span>}
                  {p.pose && <span className="preset-tag">{p.pose.replaceAll('_', ' ')}</span>}
                  {p.has_face_ref && <span className="preset-tag gold">face</span>}
                  {p.has_pose_ref && <span className="preset-tag gold">pose</span>}
                  {p.voice_id && <span className="preset-tag gold">voice</span>}
                  {p.seed != null && <span className="preset-tag">seed {p.seed}</span>}
                </div>
              </div>
              <button
                className="preset-del"
                onClick={() => del(p.id)}
                title="Delete"
                data-testid={`preset-del-${p.id}`}
              >×</button>
            </div>
          ))}
        </div>
      </aside>
    </>
  );
}

import { useEffect, useState } from 'react';

/**
 * Gallery drawer — scrolling grid of every generated portrait.
 * Clicking a thumb: sets it as the current avatar and copies its seed
 * to the seed-lock (so subsequent generations keep the same face).
 */
export default function GalleryDrawer({
  api,
  open,
  onClose,
  onSelect,   // (entry) => void
  onDelete,   // (id) => Promise
  refreshKey, // bump to re-fetch
}) {
  const [entries, setEntries] = useState(null);

  useEffect(() => {
    if (!open) return;
    setEntries(null);
    fetch(`${api}/gallery`)
      .then((r) => r.json())
      .then((d) => setEntries(d.entries || []))
      .catch(() => setEntries([]));
  }, [api, open, refreshKey]);

  const removeEntry = async (id) => {
    if (!confirm('Remove this look from the gallery?')) return;
    await onDelete(id);
    setEntries((es) => (es || []).filter((e) => e.id !== id));
  };

  if (!open) return null;

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} data-testid="gallery-backdrop" />
      <aside className="drawer gallery-drawer" data-testid="gallery-drawer">
        <div className="drawer-close">
          <div>
            <h3 className="serif">Gallery</h3>
            <div className="subtitle">{entries ? `${entries.length} looks` : 'Loading…'}</div>
          </div>
          <button className="btn ghost" onClick={onClose} data-testid="gallery-close">Close</button>
        </div>

        {entries && entries.length === 0 && (
          <div className="dim serif italic" style={{ padding: '40px 0', textAlign: 'center' }}>
            No looks yet. Pick something from the wardrobe first.
          </div>
        )}

        <div className="gallery-grid" data-testid="gallery-grid">
          {(entries || []).map((e) => (
            <div key={e.id} className="gallery-item" data-testid={`gallery-item-${e.id}`}>
              <button
                className="gallery-thumb"
                onClick={() => onSelect(e)}
                title={`${e.label}${e.seed != null ? ' · seed ' + e.seed : ''}`}
                data-testid={`gallery-thumb-${e.id}`}
              >
                <img src={`${api}/gallery/${e.id}`} alt={e.label} loading="lazy" />
              </button>
              <div className="gallery-meta">
                <div className="gallery-label" title={e.label}>{e.label}</div>
                {e.seed != null && <div className="gallery-seed">seed · {e.seed}</div>}
              </div>
              <button
                className="gallery-del"
                onClick={() => removeEntry(e.id)}
                title="Remove"
                data-testid={`gallery-del-${e.id}`}
              >×</button>
            </div>
          ))}
        </div>
      </aside>
    </>
  );
}

// TV/Video packing UI logic

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('tv-pack-form');
  if (!form) return;

  // Inject profile select (Auto + profils)
  if (!document.getElementById('tv-profile')) {
    const container = form.querySelector('.row');
    const col = document.createElement('div');
    col.className = 'col-md-6';
    col.innerHTML = `
      <label class="form-label">Profil</label>
      <select id="tv-profile" name="profile" class="form-select">
        <option value="">Auto (par nom)</option>
        <option value="HDTV_SD">HDTV SD</option>
        <option value="HDTV_720P">HDTV 720p</option>
        <option value="HDTV_1080P">HDTV 1080p</option>
        <option value="WEB_SD">WEB SD</option>
        <option value="WEB_720P">WEB 720p</option>
        <option value="WEB_1080P">WEB 1080p</option>
      </select>
    `;
    container.appendChild(col);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('tv-pack-btn');
    btn.disabled = true;
    showStatus('tv-pack-status', 'Packaging TV en cours...', 'info');

    const fd = new FormData(form);
    try {
      const resp = await fetch('/api/tv/pack', { method: 'POST', body: fd });
      const data = await resp.json();
      if (!resp.ok || !data.success) {
        throw new Error(data.error || `HTTP ${resp.status}`);
      }
      showStatus('tv-pack-status', `Release TV créée: ${data.release_name}`, 'success');
      // Refresh releases list if available
      if (typeof loadReleases === 'function') {
        loadReleases();
      } else {
        const btnRefresh = document.getElementById('refresh-releases');
        if (btnRefresh) btnRefresh.click();
      }
    } catch (err) {
      showStatus('tv-pack-status', `Erreur: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
    }
  });
});



// Gestion templates NFO (CRUD) avec Bootstrap modal et intégration API

document.addEventListener('DOMContentLoaded', () => {
  const manageBtn = document.getElementById('manage-templates-btn');
  const modalEl = document.getElementById('nfoTemplatesModal');
  if (!manageBtn || !modalEl) return;

  const modal = new bootstrap.Modal(modalEl);
  const listEl = document.getElementById('nfo-list');
  const nameInput = document.getElementById('nfo-name');
  const contentInput = document.getElementById('nfo-content');
  const btnSave = document.getElementById('nfo-btn-save');
  const btnDelete = document.getElementById('nfo-btn-delete');
  const btnNew = document.getElementById('nfo-btn-new');
  const alertEl = document.getElementById('nfo-modal-alert');

  let currentName = null;

  function showAlert(message, type = 'success') {
    alertEl.innerHTML = `<div class="alert alert-${type} alert-dismissible" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
  }

  async function refreshList() {
    listEl.innerHTML = '';
    try {
      const resp = await fetch('/api/nfo-templates');
      const data = await resp.json();
      if (!resp.ok || !data.success) throw new Error(data.error || `HTTP ${resp.status}`);
      const items = data.templates || [];
      items.forEach(item => {
        const a = document.createElement('a');
        a.href = '#';
        a.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        a.dataset.name = item.name;
        a.textContent = item.name;
        const badge = document.createElement('span');
        badge.className = 'badge bg-secondary rounded-pill';
        badge.textContent = `${item.size || 0}`;
        a.appendChild(badge);
        a.addEventListener('click', async (e) => {
          e.preventDefault();
          await loadTemplate(item.name);
        });
        listEl.appendChild(a);
      });
    } catch (err) {
      showAlert(`Erreur chargement: ${err.message}`, 'danger');
    }
  }

  async function loadTemplate(name) {
    try {
      const resp = await fetch(`/api/nfo-templates/${encodeURIComponent(name)}`);
      const data = await resp.json();
      if (!resp.ok || !data.success) throw new Error(data.error || `HTTP ${resp.status}`);
      currentName = data.name;
      nameInput.value = data.name;
      contentInput.value = data.content || '';
    } catch (err) {
      showAlert(`Erreur lecture template: ${err.message}`, 'danger');
    }
  }

  async function saveTemplate() {
    const name = (nameInput.value || '').trim();
    const content = contentInput.value || '';
    if (!name || !content) return showAlert('Nom et contenu requis', 'warning');
    try {
      const resp = await fetch('/api/nfo-templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, content }),
      });
      const data = await resp.json();
      if (!resp.ok || !data.success) throw new Error(data.error || `HTTP ${resp.status}`);
      showAlert('Template enregistré', 'success');
      currentName = name;
      await refreshList();
      await refreshTemplatesSelect(name);
    } catch (err) {
      showAlert(`Erreur sauvegarde: ${err.message}`, 'danger');
    }
  }

  async function deleteTemplate() {
    const name = (nameInput.value || '').trim();
    if (!name || name === 'default') return showAlert('Suppression interdite pour "default"', 'warning');
    if (!confirm(`Supprimer le template "${name}" ?`)) return;
    try {
      const resp = await fetch(`/api/nfo-templates/${encodeURIComponent(name)}`, { method: 'DELETE' });
      const data = await resp.json();
      if (!resp.ok || !data.success) throw new Error(data.error || `HTTP ${resp.status}`);
      showAlert('Template supprimé', 'success');
      currentName = null;
      nameInput.value = '';
      contentInput.value = '';
      await refreshList();
      await refreshTemplatesSelect(null);
    } catch (err) {
      showAlert(`Erreur suppression: ${err.message}`, 'danger');
    }
  }

  async function refreshTemplatesSelect(selectName) {
    try {
      const resp = await fetch('/api/nfo-templates');
      const data = await resp.json();
      if (!resp.ok || !data.success) return;
      const sel = document.getElementById('nfo-template');
      if (!sel) return;
      // Preserve default option
      const defaultOpt = document.createElement('option');
      defaultOpt.value = '';
      defaultOpt.textContent = 'Default';
      const current = sel.value;
      sel.innerHTML = '';
      sel.appendChild(defaultOpt);
      (data.templates || []).forEach(t => {
        if (t.name === 'default') return;
        const opt = document.createElement('option');
        opt.value = t.path;
        opt.textContent = t.name;
        sel.appendChild(opt);
      });
      if (selectName) {
        // find path matching selectName
        const opt = Array.from(sel.options).find(o => o.textContent === selectName);
        if (opt) sel.value = opt.value;
      } else {
        sel.value = current || '';
      }
    } catch {}
  }

  btnSave.addEventListener('click', saveTemplate);
  btnDelete.addEventListener('click', deleteTemplate);
  btnNew.addEventListener('click', () => {
    currentName = null;
    nameInput.value = '';
    contentInput.value = '';
  });

  manageBtn.addEventListener('click', async () => {
    showAlert('', '');
    alertEl.innerHTML = '';
    await refreshList();
    // Load selected template if any
    const sel = document.getElementById('nfo-template');
    if (sel && sel.value) {
      // try to map back to name by path
      const selectedName = sel.options[sel.selectedIndex].textContent;
      if (selectedName) await loadTemplate(selectedName);
    } else {
      // default
      await loadTemplate('default');
    }
    modal.show();
  });
});


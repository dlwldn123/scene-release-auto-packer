// Gestion upload et packaging eBooks

document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('ebook-file');
    const packSection = document.getElementById('pack-section');
    const packForm = document.getElementById('pack-form');
    
    if (!uploadArea || !fileInput || !packSection) return;
    
    // Clic sur zone upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Drag & drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // Sélection fichier
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Handler sélection fichier
    async function handleFileSelect(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        showStatus('upload-status', 'Upload et extraction métadonnées en cours...', 'info');
        
        try {
            const response = await fetch('/api/meta', {
                method: 'POST',
                body: formData,
            });
            
            const data = await response.json();
            
            if (data.success) {
                showStatus('upload-status', 'Fichier uploadé avec succès', 'success');
                
                // Afficher métadonnées
                displayMetadata(data.metadata);
                
                // Afficher section packaging
                packSection.style.display = 'block';
                packForm.dataset.filePath = data.file_path;
                
                // Charger groupes
                loadGroups();
            } else {
                showStatus('upload-status', `Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            showStatus('upload-status', `Erreur: ${error.message}`, 'error');
        }
    }
    
    // Afficher métadonnées
    function displayMetadata(metadata) {
        const preview = document.getElementById('metadata-preview');
        if (!preview) return;
        
        preview.innerHTML = `
            <h3>Métadonnées détectées:</h3>
            <dl>
                <dt>Titre:</dt>
                <dd>${metadata.title || 'N/A'}</dd>
                <dt>Auteur:</dt>
                <dd>${metadata.author || 'N/A'}</dd>
                <dt>Éditeur:</dt>
                <dd>${metadata.publisher || 'N/A'}</dd>
                <dt>Année:</dt>
                <dd>${metadata.year || 'N/A'}</dd>
                <dt>ISBN:</dt>
                <dd>${metadata.isbn || 'N/A'}</dd>
                <dt>Format:</dt>
                <dd>${metadata.format || 'N/A'}</dd>
                <dt>Langue:</dt>
                <dd>${metadata.language || 'N/A'}</dd>
            </dl>
        `;
    }
    
    // Charger groupes
    async function loadGroups() {
        const select = document.getElementById('group-select');
        if (!select) return;
        
        try {
            const [groupsData, prefsData, templatesData] = await Promise.all([
                apiRequest('/api/groups'),
                apiRequest('/api/prefs'),
                apiRequest('/api/nfo-templates'),
            ]);
            
            if (groupsData.success) {
                select.innerHTML = '<option value="">-- Sélectionner --</option>';
                
                groupsData.groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group;
                    option.textContent = group;
                    if (prefsData.success && prefsData.last_group && group === prefsData.last_group) {
                        option.selected = true;
                    }
                    select.appendChild(option);
                });
            }

            // Charger templates NFO
            const tplSelect = document.getElementById('nfo-template');
            if (tplSelect && templatesData.success) {
                // reset, garder "Default"
                const defaultOpt = tplSelect.querySelector('option[value=""]');
                tplSelect.innerHTML = '';
                if (defaultOpt) tplSelect.appendChild(defaultOpt);
                templatesData.templates.forEach(t => {
                    if (t.name === 'default') return; // default déjà présent
                    const opt = document.createElement('option');
                    opt.value = t.path; // on passe le chemin vers le backend
                    opt.textContent = t.name;
                    if (prefsData.success && prefsData.last_nfo_template && (prefsData.last_nfo_template === t.path || prefsData.last_nfo_template === t.name)) {
                        opt.selected = true;
                    }
                    tplSelect.appendChild(opt);
                });
            }
        } catch (error) {
            console.error('Erreur chargement groupes:', error);
        }
    }
    
    // Soumission formulaire packaging
    packForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const packBtn = document.getElementById('pack-btn');
        packBtn.disabled = true;
        showStatus('pack-status', 'Packaging en cours...', 'info');
        
        const formData = {
            file_path: packForm.dataset.filePath,
            group: document.getElementById('group-select').value,
            source: document.getElementById('source-select').value || null,
            url: document.getElementById('url-input').value || null,
            enable_api: document.getElementById('enable-api').checked,
            nfo_template: document.getElementById('nfo-template').value || null,
        };
        
        try {
            const data = await apiRequest('/api/pack', {
                method: 'POST',
                body: JSON.stringify(formData),
            });
            
            if (data.success) {
                showStatus('pack-status', `Release créée: ${data.release_name}`, 'success');
                // Sauver préférences serveur
                try {
                    await apiRequest('/api/prefs', {
                        method: 'POST',
                        body: JSON.stringify({
                            last_group: document.getElementById('group-select').value || null,
                            last_nfo_template: document.getElementById('nfo-template').value || null,
                        }),
                    });
                } catch {}
                loadReleases();
            } else {
                showStatus('pack-status', `Erreur: ${data.error}`, 'error');
            }
        } catch (error) {
            showStatus('pack-status', `Erreur: ${error.message}`, 'error');
        } finally {
            packBtn.disabled = false;
        }
    });
    
    // Charger releases au chargement
    if (document.getElementById('refresh-releases')) {
        document.getElementById('refresh-releases').addEventListener('click', loadReleases);
        loadReleases();
    }
    
    // Fonction charger releases
    async function loadReleases() {
        const listDiv = document.getElementById('releases-list');
        if (!listDiv) return;
        
        try {
            const data = await apiRequest('/api/releases');
            
            if (data.success) {
                if (data.releases.length === 0) {
                    listDiv.innerHTML = '<p>Aucune release créée</p>';
                    return;
                }
                
                listDiv.innerHTML = data.releases.map(release => `
                    <div class="release-card">
                        <h3>${release.name}</h3>
                        <div class="meta">
                            ${release.zip_volumes} volume(s) ZIP • ${release.rar_volumes} volume(s) RAR<br>
                            ${formatSize(release.size)}
                        </div>
                        <div>
                            <a href="/api/releases/${release.name}/download/nfo">NFO</a>
                            <a href="/api/releases/${release.name}/download/sfv">SFV</a>
                            <a href="/api/releases/${release.name}/download/zip">ZIP</a>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            listDiv.innerHTML = `<p class="status error">Erreur: ${error.message}</p>`;
        }
    }
});

// Dashboard data loading

async function loadDashboardData() {
    if (!isAuthenticated()) return;
    
    try {
        // Charger statistiques
        await Promise.all([
            loadUsersCount(),
            loadJobsCount(),
            loadReleasesCount(),
            loadRecentReleases(),
            loadRecentJobs(),
        ]);
    } catch (error) {
        console.error('Erreur chargement dashboard:', error);
    }
}

async function loadUsersCount() {
    try {
        const response = await authenticatedFetch('/api/users');
        const data = await response.json();
        if (data.success) {
            const count = data.users ? data.users.length : 0;
            document.getElementById('users-count').textContent = count;
        }
    } catch (error) {
        console.error('Erreur chargement utilisateurs:', error);
    }
}

async function loadJobsCount() {
    try {
        const response = await authenticatedFetch('/api/jobs?limit=1');
        const data = await response.json();
        if (data.success) {
            document.getElementById('jobs-count').textContent = data.total || 0;
        }
    } catch (error) {
        console.error('Erreur chargement jobs:', error);
    }
}

async function loadReleasesCount() {
    try {
        const response = await authenticatedFetch('/api/releases');
        const data = await response.json();
        if (data.success) {
            const count = data.releases ? data.releases.length : 0;
            document.getElementById('releases-count').textContent = count;
        }
    } catch (error) {
        console.error('Erreur chargement releases:', error);
    }
}

async function loadRecentReleases() {
    try {
        const response = await authenticatedFetch('/api/releases');
        const data = await response.json();
        if (data.success && data.releases) {
            const container = document.getElementById('recent-releases-list');
            if (!container) return;
            
            const releases = data.releases.slice(0, 5);
            
            if (releases.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">Aucune release</p>';
                return;
            }
            
            container.innerHTML = releases.map(release => `
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                    <div>
                        <strong>${release.name}</strong>
                        <div class="small text-muted">
                            ${release.has_nfo ? '<span class="badge bg-success">NFO</span>' : ''}
                            ${release.has_sfv ? '<span class="badge bg-info">SFV</span>' : ''}
                            ${release.zip_volumes > 0 ? `<span class="badge bg-warning">${release.zip_volumes} ZIP</span>` : ''}
                        </div>
                    </div>
                    <div class="text-end">
                        <small class="text-muted">${formatBytes(release.size)}</small>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erreur chargement releases récentes:', error);
    }
}

async function loadRecentJobs() {
    try {
        const response = await authenticatedFetch('/api/jobs?limit=5');
        const data = await response.json();
        if (data.success && data.jobs) {
            const container = document.getElementById('recent-jobs-list');
            if (!container) return;
            
            const jobs = data.jobs;
            
            if (jobs.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">Aucun job</p>';
                return;
            }
            
            container.innerHTML = jobs.map(job => {
                const statusIcon = {
                    'completed': '✓',
                    'failed': '✗',
                    'running': '⏳',
                    'pending': '⏸'
                }[job.status] || '•';
                
                const statusClass = {
                    'completed': 'text-success',
                    'failed': 'text-danger',
                    'running': 'text-warning',
                    'pending': 'text-muted'
                }[job.status] || 'text-muted';
                
                return `
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <span class="${statusClass}">${statusIcon}</span>
                            <strong>${job.job_id.substring(0, 8)}...</strong>
                            <div class="small text-muted">
                                ${job.type} | ${job.group_name}
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">${job.release_name || 'N/A'}</small>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Erreur chargement jobs récents:', error);
    }
}

function formatBytes(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Exposer globalement
window.loadDashboardData = loadDashboardData;
window.loadUsersCount = loadUsersCount;
window.loadJobsCount = loadJobsCount;
window.loadReleasesCount = loadReleasesCount;
window.loadRecentReleases = loadRecentReleases;
window.loadRecentJobs = loadRecentJobs;

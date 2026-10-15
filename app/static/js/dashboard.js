/**
 * DevOps Automation Platform - Interactive Dashboard Controller
 * Real telemetry streaming, lightweight canvas charting, and diagnostic probe runner.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- State Management ---
    let autoRefreshInterval = 5; // seconds
    let refreshTimer = null;
    let isFetching = false;

    // Rolling telemetry history for canvas charting
    const maxDataPoints = 15;
    const telemetryHistory = {
        labels: [],
        cpu: [],
        memory: []
    };

    // --- DOM Elements ---
    const utcClock = document.getElementById('utcClock');
    const refreshBtn = document.getElementById('refreshBtn');
    const autoRefreshSelect = document.getElementById('autoRefreshSelect');
    const errorBanner = document.getElementById('errorBanner');
    const errorMessage = document.getElementById('errorMessage');
    const retryFetchBtn = document.getElementById('retryFetchBtn');
    const breadcrumbSectionTitle = document.getElementById('breadcrumbSectionTitle');

    // Sidebar Mobile Controls
    const sidebar = document.getElementById('sidebar');
    const mobileToggleBtn = document.getElementById('mobileToggleBtn');
    const mobileCloseBtn = document.getElementById('mobileCloseBtn');

    // Overview Metric Elements
    const valHealthStatus = document.getElementById('valHealthStatus');
    const badgeHealth = document.getElementById('badgeHealth');
    const valUptime = document.getElementById('valUptime');
    const valCpuPercent = document.getElementById('valCpuPercent');
    const cpuProgressBar = document.getElementById('cpuProgressBar');
    const valCpuLoads = document.getElementById('valCpuLoads');
    const badgeCpuCores = document.getElementById('badgeCpuCores');
    const valMemUsed = document.getElementById('valMemUsed');
    const valMemTotal = document.getElementById('valMemTotal');
    const valMemFree = document.getElementById('valMemFree');
    const badgeMemPercent = document.getElementById('badgeMemPercent');
    const memProgressBar = document.getElementById('memProgressBar');
    const sidebarStatusText = document.getElementById('sidebarStatusText');

    // Diagnostic Console Elements
    const diagnosticUrl = document.getElementById('diagnosticUrl');
    const diagnosticStatus = document.getElementById('diagnosticStatus');
    const diagnosticPayload = document.getElementById('diagnosticPayload');
    const diagnosticLatency = document.getElementById('diagnosticLatency');
    const probeButtons = document.querySelectorAll('.diagnostic-actions button');

    // Table & Canvas Elements
    const deploymentsTableBody = document.getElementById('deploymentsTableBody');
    const resourceCanvas = document.getElementById('resourceCanvas');

    // Infrastructure Spec Elements
    const infraOs = document.getElementById('infraOs');
    const infraPlatform = document.getElementById('infraPlatform');
    const infraPython = document.getElementById('infraPython');
    const infraDisk = document.getElementById('infraDisk');

    // --- 1. UTC Clock ---
    function updateClock() {
        const now = new Date();
        const timeString = now.toISOString().slice(11, 19) + ' UTC';
        if (utcClock) utcClock.textContent = timeString;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // --- 2. Tab Navigation & Mobile Drawer ---
    const navLinks = document.querySelectorAll('.nav-link');
    const tabSections = document.querySelectorAll('.tab-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const sectionTarget = link.getAttribute('data-section');
            if (!sectionTarget) return;

            // Switch active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Switch active section
            tabSections.forEach(sec => sec.classList.remove('active'));
            const activeSection = document.getElementById(`section-${sectionTarget}`);
            if (activeSection) {
                activeSection.classList.add('active');
            }

            // Update breadcrumb
            const labelSpan = link.querySelector('span');
            if (labelSpan && breadcrumbSectionTitle) {
                breadcrumbSectionTitle.textContent = labelSpan.textContent;
            }

            // Close mobile sidebar if open
            if (sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        });
    });

    if (mobileToggleBtn) {
        mobileToggleBtn.addEventListener('click', () => {
            sidebar.classList.add('open');
        });
    }

    if (mobileCloseBtn) {
        mobileCloseBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }

    // --- 3. Telemetry Canvas Chart (Dual line: CPU & RAM) ---
    function renderChart() {
        if (!resourceCanvas) return;
        const ctx = resourceCanvas.getContext('2d');
        const width = resourceCanvas.width = resourceCanvas.parentElement.clientWidth;
        const height = resourceCanvas.height = 200;

        ctx.clearRect(0, 0, width, height);

        const padLeft = 40;
        const padRight = 20;
        const padTop = 20;
        const padBottom = 30;
        const chartWidth = width - padLeft - padRight;
        const chartHeight = height - padTop - padBottom;

        // Draw horizontal grid lines
        ctx.strokeStyle = '#243248';
        ctx.lineWidth = 1;
        ctx.font = '10px JetBrains Mono, monospace';
        ctx.fillStyle = '#64748b';
        ctx.textAlign = 'right';

        const gridSteps = 4;
        for (let i = 0; i <= gridSteps; i++) {
            const y = padTop + (chartHeight / gridSteps) * i;
            const percentLabel = `${100 - (i * 25)}%`;

            ctx.beginPath();
            ctx.moveTo(padLeft, y);
            ctx.lineTo(width - padRight, y);
            ctx.stroke();

            ctx.fillText(percentLabel, padLeft - 8, y + 3);
        }

        if (telemetryHistory.cpu.length < 2) {
            ctx.fillStyle = '#64748b';
            ctx.textAlign = 'center';
            ctx.fillText('Streaming resource telemetry...', width / 2, height / 2);
            return;
        }

        const pointCount = telemetryHistory.cpu.length;
        const xStep = chartWidth / (maxDataPoints - 1);

        // Helper to plot series
        function drawSeries(data, strokeColor, fillColor) {
            ctx.beginPath();
            const startX = padLeft + (maxDataPoints - pointCount) * xStep;

            data.forEach((val, idx) => {
                const x = startX + idx * xStep;
                const normalizedY = padTop + chartHeight * (1 - Math.min(100, Math.max(0, val)) / 100);
                if (idx === 0) {
                    ctx.moveTo(x, normalizedY);
                } else {
                    ctx.lineTo(x, normalizedY);
                }
            });

            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = 2.5;
            ctx.stroke();

            // Fill area under curve
            const lastX = startX + (data.length - 1) * xStep;
            ctx.lineTo(lastX, padTop + chartHeight);
            ctx.lineTo(startX, padTop + chartHeight);
            ctx.closePath();
            ctx.fillStyle = fillColor;
            ctx.fill();
        }

        // Draw Memory Series (Indigo)
        drawSeries(
            telemetryHistory.memory,
            '#6366f1',
            'rgba(99, 102, 241, 0.12)'
        );

        // Draw CPU Series (Emerald)
        drawSeries(
            telemetryHistory.cpu,
            '#10b981',
            'rgba(16, 185, 129, 0.15)'
        );
    }

    window.addEventListener('resize', renderChart);

    // --- 4. Format Uptime Utility ---
    function formatUptime(seconds) {
        if (typeof seconds !== 'number' || isNaN(seconds)) return '--';
        const d = Math.floor(seconds / (3600 * 24));
        const h = Math.floor((seconds % (3600 * 24)) / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;

        if (d > 0) return `${d}d ${h}h ${m}m`;
        if (h > 0) return `${h}h ${m}m ${s}s`;
        if (m > 0) return `${m}m ${s}s`;
        return `${s}s`;
    }

    // --- 5. Data Fetching Layer ---
    async function fetchTelemetry() {
        if (isFetching) return;
        isFetching = true;
        if (refreshBtn) refreshBtn.classList.add('refreshing');

        try {
            // Concurrent fetch of all live endpoints
            const [healthRes, metricsRes, infoRes, deployRes] = await Promise.all([
                fetch('/health'),
                fetch('/api/v1/system/metrics'),
                fetch('/api/v1/info'),
                fetch('/api/v1/deployments')
            ]);

            if (!healthRes.ok || !metricsRes.ok) {
                throw new Error(`API returned HTTP ${healthRes.status}/${metricsRes.status}`);
            }

            const healthData = await healthRes.json();
            const metricsData = await metricsRes.json();
            const infoData = infoRes.ok ? await infoRes.json() : {};
            const deployData = deployRes.ok ? await deployRes.json() : { deployments: [] };

            // Hide Error Banner on Success
            if (errorBanner) errorBanner.classList.add('hidden');

            // Update Health Card
            if (valHealthStatus) valHealthStatus.textContent = healthData.status ? healthData.status.toUpperCase() : 'ONLINE';
            if (valUptime) valUptime.textContent = formatUptime(healthData.uptime_seconds);
            if (sidebarStatusText) sidebarStatusText.textContent = 'System Online';

            // Update CPU Card
            if (metricsData.cpu) {
                const cpuPct = metricsData.cpu.percent || 0;
                if (valCpuPercent) valCpuPercent.textContent = `${cpuPct}%`;
                if (cpuProgressBar) cpuProgressBar.style.width = `${Math.min(100, cpuPct)}%`;
                if (badgeCpuCores) badgeCpuCores.textContent = `${metricsData.cpu.cores} Cores`;
                if (valCpuLoads) {
                    valCpuLoads.textContent = `${metricsData.cpu.load_1m}, ${metricsData.cpu.load_5m}, ${metricsData.cpu.load_15m}`;
                }

                // Add to chart history
                telemetryHistory.cpu.push(cpuPct);
                if (telemetryHistory.cpu.length > maxDataPoints) telemetryHistory.cpu.shift();
            }

            // Update Memory Card
            if (metricsData.memory) {
                const memPct = metricsData.memory.percent || 0;
                if (valMemUsed) valMemUsed.textContent = `${Math.round(metricsData.memory.used_mb)} MB`;
                if (valMemTotal) valMemTotal.textContent = `${Math.round(metricsData.memory.total_mb)} MB`;
                if (valMemFree) valMemFree.textContent = `${Math.round(metricsData.memory.available_mb)} MB`;
                if (badgeMemPercent) badgeMemPercent.textContent = `${memPct}%`;
                if (memProgressBar) memProgressBar.style.width = `${Math.min(100, memPct)}%`;

                // Add to chart history
                telemetryHistory.memory.push(memPct);
                if (telemetryHistory.memory.length > maxDataPoints) telemetryHistory.memory.shift();
            }

            // Update Host & Infrastructure View
            if (infoData.system && infraOs) infraOs.textContent = infoData.system;
            if (infoData.platform && infraPlatform) infraPlatform.textContent = infoData.platform;
            if (infoData.python_version && infraPython) infraPython.textContent = `Python ${infoData.python_version}`;
            if (metricsData.disk && infraDisk) {
                infraDisk.textContent = `${metricsData.disk.used_gb} GB / ${metricsData.disk.total_gb} GB (${metricsData.disk.percent}%)`;
            }

            // Update Deployments Table
            if (deploymentsTableBody && deployData.deployments) {
                deploymentsTableBody.innerHTML = deployData.deployments.map(item => `
                    <tr>
                        <td><span class="commit-badge">${escapeHtml(item.commit)}</span></td>
                        <td><strong>${escapeHtml(item.message)}</strong></td>
                        <td>${escapeHtml(item.author)}</td>
                        <td><span class="badge badge-info">${escapeHtml(item.phase || 'Phase 1')}</span></td>
                        <td><span class="badge badge-success">&#10003; ${escapeHtml(item.status)}</span></td>
                        <td class="text-muted">${escapeHtml(item.time_ago)}</td>
                    </tr>
                `).join('');
            }

            // Render updated chart
            renderChart();

        } catch (err) {
            console.error('Telemetry fetch failure:', err);
            if (errorBanner) {
                errorBanner.classList.remove('hidden');
                if (errorMessage) errorMessage.textContent = `Failed to connect to platform API: ${err.message}`;
            }
            if (sidebarStatusText) sidebarStatusText.textContent = 'Degraded';
        } finally {
            isFetching = false;
            if (refreshBtn) refreshBtn.classList.remove('refreshing');
        }
    }

    // Helper for safe HTML rendering
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // --- 6. Interactive Diagnostic Console Runner ---
    async function testEndpoint(endpoint) {
        const startTime = performance.now();
        if (diagnosticUrl) diagnosticUrl.textContent = `GET ${endpoint}`;
        if (diagnosticStatus) diagnosticStatus.textContent = 'Executing...';
        if (diagnosticPayload) diagnosticPayload.textContent = 'Sending request to server...';

        try {
            const response = await fetch(endpoint);
            const duration = Math.round(performance.now() - startTime);
            const data = await response.json();

            if (diagnosticLatency) diagnosticLatency.textContent = `Latency: ${duration} ms`;
            if (diagnosticStatus) {
                diagnosticStatus.textContent = `HTTP ${response.status} ${response.statusText || 'OK'}`;
                diagnosticStatus.className = response.ok ? 'terminal-status text-success' : 'terminal-status text-danger';
            }
            if (diagnosticPayload) {
                diagnosticPayload.textContent = JSON.stringify(data, null, 2);
            }
        } catch (err) {
            const duration = Math.round(performance.now() - startTime);
            if (diagnosticLatency) diagnosticLatency.textContent = `Latency: ${duration} ms`;
            if (diagnosticStatus) {
                diagnosticStatus.textContent = 'Network Error';
                diagnosticStatus.className = 'terminal-status text-danger';
            }
            if (diagnosticPayload) {
                diagnosticPayload.textContent = `Error: ${err.message}`;
            }
        }
    }

    probeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            probeButtons.forEach(b => b.classList.remove('active-probe-btn'));
            btn.classList.add('active-probe-btn');
            const targetEndpoint = btn.getAttribute('data-endpoint');
            if (targetEndpoint) testEndpoint(targetEndpoint);
        });
    });

    // --- 7. Refresh Controls & Scheduling ---
    function setupAutoRefresh() {
        if (refreshTimer) clearInterval(refreshTimer);
        if (autoRefreshInterval > 0) {
            refreshTimer = setInterval(fetchTelemetry, autoRefreshInterval * 1000);
        }
    }

    if (autoRefreshSelect) {
        autoRefreshSelect.addEventListener('change', (e) => {
            autoRefreshInterval = parseInt(e.target.value, 10);
            setupAutoRefresh();
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            fetchTelemetry();
        });
    }

    if (retryFetchBtn) {
        retryFetchBtn.addEventListener('click', () => {
            fetchTelemetry();
        });
    }

    // --- 8. Initial Bootstrap ---
    fetchTelemetry();
    setupAutoRefresh();
    // Default test run for diagnostic console
    testEndpoint('/health');
});

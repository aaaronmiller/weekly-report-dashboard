(function() {
  'use strict';
  const data = window.__WEEKLY__;
  if (!data) return;

  const weeks = (data.weeks || []).slice().sort((a,b) => a.week_ending.localeCompare(b.week_ending));
  const labels = weeks.map(w => w.week_ending);

  // Section 1: Utilities
  const escapeHTML = (str) => {
    if (!str) return '';
    return String(str).replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag));
  };
  const getSelectedWeek = () => {
    const sel = document.getElementById('week-selector');
    return sel ? sel.value : (weeks.length ? weeks[weeks.length-1].week_ending : null);
  };
  const baseChartOption = (title) => ({
    title: { text: title, textStyle: { color: '#f7f8f8', fontSize: 13, fontWeight: 'normal' } },
    backgroundColor: 'transparent',
    textStyle: { color: '#8a8f98' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', axisLabel: { color: '#8a8f98' } },
    yAxis: { type: 'value', axisLabel: { color: '#8a8f98' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
    grid: { left: 50, right: 20, top: 40, bottom: 30 }
  });

  // Section 2: Attention Panel
  const renderAttentionPanel = () => {
    const openItems = (data.carry_over || []).filter(c => c.state !== 'completed');
    const stalledItems = openItems.filter(c => c.state === 'stalled');
    const maxStallAge = stalledItems.length ? Math.max(...stalledItems.map(c => c.carry_age)) : 0;
    const stalledEl = document.getElementById('attention-stalled');
    if (stalledEl) {
      stalledEl.querySelector('.card-value').textContent = stalledItems.length;
      stalledEl.querySelector('.card-detail').textContent = maxStallAge > 0 ? `Oldest: ${maxStallAge}w` : 'All good';
      stalledEl.className = 'attention-card severity-' + (stalledItems.length > 3 ? 'high' : stalledItems.length > 0 ? 'med' : 'low');
    }

    const darkWeeks = weeks.filter(w => w.is_dark_work);
    const recentDark = darkWeeks.length ? darkWeeks[darkWeeks.length - 1].week_ending : 'None';
    const darkEl = document.getElementById('attention-darkwork');
    if (darkEl) {
      darkEl.querySelector('.card-value').textContent = darkWeeks.length;
      darkEl.querySelector('.card-detail').textContent = `Recent: ${recentDark}`;
      darkEl.className = 'attention-card severity-' + (darkWeeks.length > 2 ? 'high' : darkWeeks.length > 0 ? 'med' : 'low');
    }

    const cov = data.coverage || {};
    const covEl = document.getElementById('attention-coverage');
    if (covEl) {
      covEl.querySelector('.card-value').textContent = `${cov.with_both || 0} / ${cov.weeks_total || 0}`;
      covEl.querySelector('.card-detail').textContent = `Pair: ${cov.with_pair || 0}, Bundle: ${cov.with_bundle || 0}`;
      covEl.className = 'attention-card severity-' + (cov.missing === 0 ? 'low' : cov.missing < 3 ? 'med' : 'high');
    }

    const proj = data.project_activity || [];
    const recent4Weeks = labels.slice(-4);
    const recentProj = new Set(proj.filter(p => recent4Weeks.includes(p.week_ending) && (p.commits > 0 || p.sessions > 0)).map(p => p.project_name));
    const allProj = new Set(proj.map(p => p.project_name));
    const neglectedCount = Math.max(0, allProj.size - recentProj.size);
    const negEl = document.getElementById('attention-neglected');
    if (negEl) {
      negEl.querySelector('.card-value').textContent = neglectedCount;
      negEl.querySelector('.card-detail').textContent = `${recentProj.size} active`;
      negEl.className = 'attention-card severity-' + (neglectedCount > 10 ? 'high' : neglectedCount > 5 ? 'med' : 'info');
    }

    const git = data.git_stats || {};
    const gitEl = document.getElementById('attention-git');
    if (gitEl) {
      const repos = git.repositories || [];
      const dirty = repos.filter(r => r.uncommitted > 0).length;
      const behind = repos.filter(r => r.behind > 0).length;
      gitEl.querySelector('.card-value').textContent = dirty + behind;
      gitEl.querySelector('.card-detail').textContent = `${dirty} dirty, ${behind} behind`;
      gitEl.className = 'attention-card severity-' + ((dirty + behind) > 3 ? 'high' : (dirty + behind) > 0 ? 'med' : 'low');
    }

    const genAt = data.generated_at;
    const freshEl = document.getElementById('attention-freshness');
    if (freshEl) {
      if (genAt) {
        const diffDays = (new Date() - new Date(genAt)) / (1000 * 60 * 60 * 24);
        freshEl.querySelector('.card-value').textContent = diffDays < 1 ? 'Today' : `${Math.floor(diffDays)}d`;
        freshEl.querySelector('.card-detail').textContent = genAt.split('T')[0];
        freshEl.className = 'attention-card severity-' + (diffDays < 3 ? 'low' : diffDays < 7 ? 'med' : 'high');
      } else {
        freshEl.querySelector('.card-value').textContent = 'N/A';
        freshEl.className = 'attention-card severity-info';
      }
    }
  };

  // Section 3: Action Items
  const renderActionItems = () => {
    const aiEl = document.getElementById('action-items');
    if (!aiEl) return;
    let html = '';
    
    const proj = data.project_activity || [];
    const recentWk = labels[labels.length - 1];
    proj.filter(p => p.week_ending === recentWk && p.uncommitted_count > 0).forEach(p => {
      html += `<div class="action-item"><span class="action-type push">PUSH</span> ${p.project_name} has ${p.uncommitted_count} uncommitted changes</div>`;
    });
    
    const git = data.git_stats || {};
    const repos = git.repositories || [];
    repos.filter(r => r.behind > 0).forEach(r => {
      html += `<div class="action-item"><span class="action-type pull">PULL</span> ${r.name} is ${r.behind} commits behind</div>`;
    });
    
    const openItems = (data.carry_over || []).filter(c => c.state !== 'completed');
    openItems.filter(c => c.state === 'stalled' && c.carry_age >= 6).forEach(c => {
      html += `<div class="action-item"><span class="action-type retire">RETIRE</span> "${escapeHTML(c.item_text)}" (Age: ${c.carry_age}w)</div>`;
    });
    
    weeks.filter(w => w.is_dark_work).slice(-3).forEach(w => {
      html += `<div class="action-item"><span class="action-type review">REVIEW</span> Dark work week: ${w.week_ending} (${w.sessions_per_commit?.toFixed(1) || '?'} SPC)</div>`;
    });
    
    const listEl = document.createElement('div');
    if (!html) html = '<div class="action-item" style="color:var(--muted);">No immediate action items.</div>';
    listEl.innerHTML = html;
    
    // preserve the title inside action-items
    const title = aiEl.querySelector('h3');
    aiEl.innerHTML = '';
    if(title) aiEl.appendChild(title);
    aiEl.appendChild(listEl);
  };

  // Section 4: Table search/sort
  const initTable = () => {
    const table = document.getElementById('canonical-table');
    const search = document.getElementById('table-search');
    if (!table || !search) return;
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr'));
    let sortDir = 1;
    let sortCol = 0;
    search.addEventListener('input', () => {
      const q = search.value.toLowerCase();
      rows.forEach(r => {
        r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
    const headers = table.querySelectorAll('th');
    headers.forEach((th, idx) => {
      th.addEventListener('click', () => {
        if (sortCol === idx) sortDir *= -1; else { sortCol = idx; sortDir = 1; }
        const sorted = rows.slice().sort((a,b) => {
          const av = a.cells[idx] ? a.cells[idx].textContent.trim() : '';
          const bv = b.cells[idx] ? b.cells[idx].textContent.trim() : '';
          const an = parseFloat(av), bn = parseFloat(bv);
          if (!isNaN(an) && !isNaN(bn)) return (an - bn) * sortDir;
          return av.localeCompare(bv) * sortDir;
        });
        sorted.forEach(r => tbody.appendChild(r));
      });
    });
  };

  // Section 5: Core figures 1-4
  const renderFigure1 = (el) => {
    if (!el || typeof echarts === 'undefined') return;
    const option = baseChartOption('Figure 1 — Throughput Trend');
    option.legend = { data: ['Sessions','Commits','Files','Projects'], textStyle: { color: '#8a8f98' } };
    option.xAxis.data = labels;
    option.yAxis = { type: 'log', logBase: 10, name: 'log scale', axisLabel: { color: '#8a8f98' } };
    option.series = [
      {name: 'Sessions', type: 'line', data: weeks.map(w => w.sessions), itemStyle: { color: '#7170ff' }},
      {name: 'Commits', type: 'line', data: weeks.map(w => w.commits), itemStyle: { color: '#ff7a7a' }},
      {name: 'Files', type: 'line', data: weeks.map(w => w.files_changed), itemStyle: { color: '#4ecdc4' }},
      {name: 'Projects', type: 'line', data: weeks.map(w => w.projects_active), itemStyle: { color: '#ffb020' }}
    ];
    const chart = echarts.getInstanceByDom(el) || echarts.init(el, 'dark');
    chart.setOption(option);
    el._chart = chart;
  };

  const renderFigure2 = (el) => {
    if (!el || typeof echarts === 'undefined') return;
    const option = baseChartOption('Figure 2 — Dark Work (SPC)');
    option.xAxis.data = labels;
    option.yAxis.name = 'sessions / commit';
    const threshold = data.config?.dark_work_threshold || 8.0;
    option.series = [{
      name: 'SPC', type: 'line', data: weeks.map(w => w.sessions_per_commit),
      itemStyle: { color: '#ffb020' },
      markLine: { data: [{ yAxis: threshold, name: 'threshold' }], lineStyle: { color: '#ff4d4d' } }
    }];
    const chart = echarts.getInstanceByDom(el) || echarts.init(el, 'dark');
    chart.setOption(option);
    el._chart = chart;
  };

  const renderFigure3 = () => {
    const el = document.getElementById('figure3');
    if (!el || typeof echarts === 'undefined') return;
    const wk = getSelectedWeek();
    const rec = weeks.find(w => w.week_ending === wk);
    if (!rec || !rec.daily_sessions) return;
    const daily = rec.daily_sessions;
    const option = baseChartOption('Figure 3 — Daily Sessions ('+wk+')');
    option.xAxis.data = daily.map(d => d.date);
    option.series = [{
      name: 'Sessions', type: 'bar', data: daily.map(d => d.sessions), itemStyle: { color: '#7170ff' }
    }];
    const chart = echarts.getInstanceByDom(el) || echarts.init(el, 'dark');
    chart.setOption(option);
  };

  const renderFigure4 = () => {
    const el = document.getElementById('figure4');
    if (!el || typeof echarts === 'undefined') return;
    const wk = getSelectedWeek();
    const acts = (data.project_activity || []).filter(p => p.week_ending === wk);
    const option = baseChartOption('Figure 4 — Project Activity ('+wk+')');
    option.xAxis.data = acts.map(a => a.project_name);
    option.legend = { data: ['Commits','Uncommitted'], textStyle: { color: '#8a8f98' } };
    option.series = [
      { name: 'Commits', type: 'bar', data: acts.map(a => a.commits || 0), itemStyle: { color: '#4ecdc4' } },
      { name: 'Uncommitted', type: 'bar', data: acts.map(a => a.uncommitted_count || 0), itemStyle: { color: '#ffb020' } }
    ];
    const chart = echarts.getInstanceByDom(el) || echarts.init(el, 'dark');
    chart.setOption(option);
  };

  // Section 6: Carry-over ledger (tabbed)
  const renderLedger = () => {
    const wrap = document.getElementById('ledger-container') || document.getElementById('ledger');
    if (!wrap) return;
    
    // TABS setup
    let currentTab = wrap.dataset.tab || 'open';
    
    const renderContent = () => {
      const items = data.carry_over || [];
      let html = '';
      if (currentTab === 'open') {
        const open = items.filter(c => c.state !== 'completed').sort((a,b) => b.carry_age - a.carry_age);
        open.forEach(it => {
          const ageClass = it.carry_age >= 5 ? 'age-high' : (it.carry_age >= 3 ? 'age-med' : 'age-low');
          const stalled = it.carry_age >= (data.config?.stall_age || 3) ? ' stalled' : '';
          html += `<div class="ledger-item${stalled}"><span class="age-badge ${ageClass}">${it.carry_age}</span><span class="item-text">${escapeHTML(it.item_text)}</span><span class="item-project">${escapeHTML(it.project_heading)}</span></div>`;
        });
      } else if (currentTab === 'completed') {
        const done = items.filter(c => c.state === 'completed');
        done.forEach(it => {
          html += `<div class="ledger-item"><span class="age-badge age-low">✓</span><span class="item-text">${escapeHTML(it.item_text)}</span><span class="item-project">${escapeHTML(it.project_heading)}</span></div>`;
        });
      } else if (currentTab === 'project') {
        const byProj = {};
        items.filter(c => c.state !== 'completed').forEach(it => {
          byProj[it.project_heading] = byProj[it.project_heading] || [];
          byProj[it.project_heading].push(it);
        });
        Object.keys(byProj).sort().forEach(proj => {
          html += `<div style="padding:var(--sp-2) var(--sp-3);background:rgba(255,255,255,0.02);font-weight:bold;">${escapeHTML(proj)}</div>`;
          byProj[proj].forEach(it => {
            const ageClass = it.carry_age >= 5 ? 'age-high' : (it.carry_age >= 3 ? 'age-med' : 'age-low');
            html += `<div class="ledger-item"><span class="age-badge ${ageClass}">${it.carry_age}</span><span class="item-text">${escapeHTML(it.item_text)}</span></div>`;
          });
        });
      }
      if (!html) html = '<div style="padding:var(--sp-4);color:var(--muted);">No items found.</div>';
      
      const contentEl = wrap.querySelector('.ledger-content') || document.createElement('div');
      contentEl.className = 'ledger-content';
      contentEl.innerHTML = html;
      
      if (!wrap.querySelector('.ledger-tabs')) {
        const tabsEl = document.createElement('div');
        tabsEl.className = 'ledger-tabs';
        ['open', 'completed', 'project'].forEach(t => {
          const btn = document.createElement('button');
          btn.className = `ledger-tab ${currentTab === t ? 'active' : ''}`;
          btn.textContent = t.charAt(0).toUpperCase() + t.slice(1);
          btn.onclick = () => { wrap.dataset.tab = t; renderLedger(); };
          tabsEl.appendChild(btn);
        });
        wrap.innerHTML = '';
        wrap.appendChild(tabsEl);
        wrap.appendChild(contentEl);
      } else {
        wrap.querySelectorAll('.ledger-tab').forEach(b => b.classList.toggle('active', b.textContent.toLowerCase() === currentTab));
        wrap.querySelector('.ledger-content').innerHTML = html;
      }
    };
    renderContent();
  };

  // Section 7: Algorithm dropdowns
  const initDropdowns = () => {
    ['algo-source', 'algo-carry', 'algo-dark', 'algo-curate', 'algo-norm'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', () => {
        // Just trigger prose & charts refresh for now
        renderProse();
        const sel = document.getElementById('algo-source');
        if (sel && sel.value === 'legacy') {
           // hide non-primary in table
           const rows = document.querySelectorAll('#canonical-table tbody tr');
           weeks.forEach((w, idx) => {
             if (rows[idx]) {
               rows[idx].style.display = (w.has_bundle || w.has_pair) ? '' : 'none';
             }
           });
        }
      });
    });
  };

  // Section 8: Data source panels (lazy)
  const renderPanelFreshness = (panel, dt) => {
    const summaryEl = panel.querySelector('.panel-summary');
    if (!summaryEl || !dt) return;
    const diffDays = (new Date() - new Date(dt)) / (1000 * 60 * 60 * 24);
    let fClass = diffDays < 3 ? 'fresh' : diffDays < 7 ? 'stale' : 'old';
    let text = diffDays < 1 ? 'Today' : `${Math.floor(diffDays)}d ago`;
    summaryEl.innerHTML = `<span class="freshness-badge ${fClass}">${text}</span>`;
  };

  const panelRenderers = {
    'panel-projects': (el) => {
      const ds = data.projects_stats;
      if (!ds) return;
      renderPanelFreshness(el, data.generated_at);
      const c = el.querySelector('.chart-lazy');
      if (c && typeof echarts !== 'undefined') {
        const top = ds.projects.slice(0, 10).reverse();
        const opt = baseChartOption('Top Projects by Commits');
        opt.xAxis = { type: 'value' };
        opt.yAxis = { type: 'category', data: top.map(p => p.project) };
        opt.series = [{ type: 'bar', data: top.map(p => p.commits || 0), itemStyle: { color: '#7170ff' } }];
        echarts.init(c, 'dark').setOption(opt);
      }
    },
    'panel-git': (el) => {
      const ds = data.git_stats;
      if (!ds) return;
      renderPanelFreshness(el, ds.generated_at || data.generated_at);
      const c = el.querySelector('.chart-lazy');
      if (c && typeof echarts !== 'undefined') {
        const opt = baseChartOption('Git Repo States');
        const counts = { clean: 0, dirty: 0, behind: 0 };
        (ds.repositories || []).forEach(r => {
          if (r.uncommitted > 0) counts.dirty++;
          else if (r.behind > 0) counts.behind++;
          else counts.clean++;
        });
        opt.series = [{ type: 'pie', radius: '60%', data: Object.entries(counts).map(([k,v]) => ({name:k, value:v})) }];
        opt.xAxis = undefined; opt.yAxis = undefined;
        echarts.init(c, 'dark').setOption(opt);
      }
    },
    'panel-harness': (el) => {
      const ds = data.harness_stats;
      if (!ds) return;
      renderPanelFreshness(el, data.generated_at);
      const c = el.querySelector('.chart-lazy');
      if (c && typeof echarts !== 'undefined') {
        const opt = baseChartOption('Sessions per Harness');
        opt.xAxis.data = ds.harness.map(h => h.harness);
        opt.series = [{ type: 'bar', data: ds.harness.map(h => h.sessions), itemStyle: { color: '#4ecdc4' } }];
        echarts.init(c, 'dark').setOption(opt);
      }
    },
    'panel-claude': (el) => {
      const ds = data.claude_stats;
      if (!ds) return;
      renderPanelFreshness(el, data.generated_at);
      const c = el.querySelector('.chart-lazy, #figure-cc1, #figure-c1');
      if (c && typeof echarts !== 'undefined') {
        const opt = baseChartOption('Claude Daily Activity');
        opt.xAxis.data = ds.days.map(d => d.date.slice(5));
        opt.series = [{ name: 'Messages', type: 'bar', data: ds.days.map(d => d.messages), itemStyle: { color: '#ffb020' } }];
        echarts.init(c, 'dark').setOption(opt);
      }
    },
    'panel-obsidian': (el) => {
      const ds = data.obsidian_stats;
      if (!ds) return;
      renderPanelFreshness(el, data.generated_at);
      const c = el.querySelector('.chart-lazy');
      if (c && typeof echarts !== 'undefined') {
        const opt = baseChartOption('Obsidian Notes per Month');
        opt.xAxis.data = ds.months.map(m => m.month);
        opt.series = [{ type: 'line', data: ds.months.map(m => m.docs), itemStyle: { color: '#a0e8af' } }];
        echarts.init(c, 'dark').setOption(opt);
      }
    },
    'panel-browser': (el) => {
      const ds = data.browser_stats;
      if (!ds) return;
      renderPanelFreshness(el, data.generated_at);
      const c = el.querySelector('.chart-lazy, #figure-br1, #figure-b1');
      if (c && typeof echarts !== 'undefined') {
        const opt = baseChartOption('Top Domains');
        const doms = (ds.top_domains||[]).slice(0, 10).reverse();
        opt.xAxis = { type: 'value' };
        opt.yAxis = { type: 'category', data: doms.map(d => d[0]) };
        opt.series = [{ type: 'bar', data: doms.map(d => d[1]), itemStyle: { color: '#7170ff' } }];
        echarts.init(c, 'dark').setOption(opt);
      }
    },
    'panel-system': (el) => {
      const ds = data.system_stats;
      if (!ds) return;
      renderPanelFreshness(el, data.generated_at);
      const c = el.querySelector('.chart-lazy');
      if (c && typeof echarts !== 'undefined') {
        const opt = baseChartOption('Upgrades per Month');
        opt.xAxis.data = (ds.upgrades_by_month||[]).map(u => u.month);
        opt.series = [{ type: 'bar', data: (ds.upgrades_by_month||[]).map(u => u.packages), itemStyle: { color: '#ff7a7a' } }];
        echarts.init(c, 'dark').setOption(opt);
      }
    },
    'panel-subvalue': (el) => {
      const ds = data.subscription_value;
      if (!ds) return;
      renderPanelFreshness(el, data.generated_at);
      const c = el.querySelector('.chart-lazy');
      if (c && typeof echarts !== 'undefined') {
        const opt = baseChartOption('Market Value vs Cost');
        opt.xAxis.data = ds.months.map(m => m.month);
        opt.series = [
          { name: 'Market Value', type: 'bar', data: ds.months.map(m => m.market_value), itemStyle: { color: '#4ecdc4' } },
          { name: 'Cost', type: 'line', data: ds.months.map(m => m.sub_cost), itemStyle: { color: '#8a8f98' } }
        ];
        echarts.init(c, 'dark').setOption(opt);
      }
    }
  };

  // Section 9: Weekly reports browser
  const renderReportsBrowser = () => {
    const list = document.getElementById('reports-list');
    const detail = document.getElementById('reports-detail');
    const weeklySummary = document.getElementById('weekly-summary');
    if (!list || !detail) return;

    // Populate weekly summary with latest week that has prose
    if (weeklySummary) {
      const latestWithProse = weeks.slice().reverse().find(w => w.prose_html);
      if (latestWithProse) {
        const theme = (latestWithProse.prose_html.match(/<p>Subject:([^<]+)/) || [])[1];
        weeklySummary.innerHTML = '<strong>Latest: ' + latestWithProse.week_ending + '</strong>' +
          (theme ? ' — ' + theme.trim() : '') +
          ' <span style="color:#8a8f98;font-size:11px;">Click a week below to read the full report.</span>';
      } else {
        weeklySummary.textContent = 'No reports in corpus yet.';
      }
    }

    let html = '<table style="width:100%;border-collapse:collapse;"><tbody>';
    weeks.slice().reverse().forEach(w => {
      const hasReport = !!w.prose_html;
      const style = hasReport ? '' : 'color:#8a8f98;';
      html += '<tr data-week="' + w.week_ending + '" style="cursor:' + (hasReport ? 'pointer' : 'default') + ';border-bottom:1px solid rgba(255,255,255,0.05);' + style + '"><td style="padding:var(--sp-2)">' + w.week_ending + '</td><td>' + w.coverage + '</td><td style="font-size:11px;color:#8a8f98;">' + (hasReport ? 'report' : 'no report') + '</td></tr>';
    });
    html += '</tbody></table>';
    list.innerHTML = html;

    list.querySelectorAll('tr').forEach(tr => {
      tr.addEventListener('click', () => {
        const wk = tr.dataset.week;
        const rec = weeks.find(x => x.week_ending === wk);
        if (rec && rec.prose_html) {
          detail.innerHTML = '<h3>' + wk + '</h3><div>' + rec.prose_html + '</div>';
        }
      });
    });
  };

  const renderProse = () => {
    const wk = getSelectedWeek();
    const rec = weeks.find(w => w.week_ending === wk);
    const prose = document.getElementById('prose') || document.getElementById('prose-panel');
    if (!prose || !rec) return;
    prose.innerHTML = `<h3>Week ${wk}</h3><div class="prose-content">${rec.prose_html || '—'}</div>`;
  };

  // Section 10: LLM supplement
  // Optionally handle LLM supplement here
  
  // Section 11: Diagnostics
  const renderDiagnostics = () => {
    const diag = document.getElementById('diagnostics');
    if (!diag) return;
    
    const asserts = data.assertions || [];
    const passed = asserts.filter(a => a.passed).length;
    const failed = asserts.length - passed;
    const qCount = weeks.filter(w => w.data_quality === 'verified').length;
    
    diag.innerHTML = `
      <div class="diagnostics-grid">
        <div class="diag-card">
          <div class="diag-value ${failed > 0 ? 'assertion-fail' : 'assertion-pass'}">${passed}/${asserts.length}</div>
          <div class="diag-label">Assertions</div>
        </div>
        <div class="diag-card">
          <div class="diag-value">${qCount}</div>
          <div class="diag-label">Verified Weeks</div>
        </div>
      </div>
    `;
  };
  const initLazyCharts = () => {
    if (typeof IntersectionObserver === 'undefined') {
      // No observer support: show everything immediately.
      document.querySelectorAll('.chart-lazy').forEach(c => c.classList.add('loaded'));
      Object.keys(panelRenderers).forEach(pid => {
        const panel = document.getElementById(pid);
        if (panel && panelRenderers[pid]) { try { panelRenderers[pid](panel); } catch (e) {} }
      });
      return;
    }
    const chartObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        chartObserver.unobserve(el);
        // Visibility first: a failed render must not leave the chart invisible.
        el.classList.add('loaded');
        if (el._chartInit) return;
        el._chartInit = true;
        try {
          if (el.id === 'figure1') renderFigure1(el);
          else if (el.id === 'figure2') renderFigure2(el);
          else {
            const panelId = el.closest('details')?.id;
            if (panelId && panelRenderers[panelId]) panelRenderers[panelId](el.closest('details'));
          }
        } catch (e) {
          el.innerHTML = '<p style="color:#ff7a7a;font-size:12px;padding:12px;">chart failed: ' + escapeHTML(String(e.message || e)) + '</p>';
        }
      });
    }, { rootMargin: '200px' });

    document.querySelectorAll('.chart-lazy').forEach(c => chartObserver.observe(c));

    document.querySelectorAll('details.data-panel').forEach(panel => {
      panel.addEventListener('toggle', () => {
        if (!panel.open) return;
        panel.querySelectorAll('.chart-lazy').forEach(c => c.classList.add('loaded'));
        if (panelRenderers[panel.id]) {
          try { panelRenderers[panel.id](panel); } catch (e) {
            const first = panel.querySelector('.chart-lazy');
            if (first) first.innerHTML = '<p style="color:#ff7a7a;font-size:12px;padding:12px;">chart failed: ' + escapeHTML(String(e.message || e)) + '</p>';
          }
        }
      });
    });
  };

  // Section 13: Init
  const init = () => {
    const banner = document.getElementById('failure-banner');
    const failed = (data.assertions || []).filter(a => !a.passed);
    if (banner && failed.length) {
      banner.classList.add('visible');
      banner.style.display = 'block';
      banner.innerHTML = '<strong>Assertions failed:</strong> ' + failed.map(a => a.assertion_id).join(' | ');
    }
    
    renderAttentionPanel();
    renderActionItems();
    initTable();
    
    renderFigure1(document.getElementById('figure1'));
    renderFigure2(document.getElementById('figure2'));
    
    const sel = document.getElementById('week-selector');
    if (sel) sel.addEventListener('change', () => { renderFigure3(); renderFigure4(); renderProse(); });
    renderFigure3();
    renderFigure4();
    
    renderLedger();
    initDropdowns();
    renderProse();
    renderReportsBrowser();
    // Populate panel summaries at init so users can see what's inside without opening
    const panelMeta = {
      'panel-projects': { label: 'Top projects by commits', dsKey: 'projects_stats' },
      'panel-git': { label: 'Repo states and health', dsKey: 'git_stats' },
      'panel-harness': { label: 'Sessions per harness', dsKey: 'harness_stats' },
      'panel-claude': { label: 'Daily Claude activity', dsKey: 'claude_stats' },
      'panel-obsidian': { label: 'Vault notes and tags', dsKey: 'obsidian_stats' },
      'panel-browser': { label: 'Browsing and YouTube', dsKey: 'browser_stats' },
      'panel-system': { label: 'Cron, upgrades, uptime', dsKey: 'system_stats' },
      'panel-subvalue': { label: 'Plan value vs cost', dsKey: 'subscription_value' },
    };
    Object.entries(panelMeta).forEach(([pid, meta]) => {
      const panel = document.getElementById(pid);
      if (!panel) return;
      const sumEl = panel.querySelector('.panel-summary');
      if (!sumEl) return;
      const ds = data[meta.dsKey];
      const hasData = ds && Object.keys(ds).length > 0;
      const genAt = data.generated_at;
      let badge = '';
      if (hasData && genAt) {
        const diffDays = (new Date() - new Date(genAt)) / (1000 * 60 * 60 * 24);
        const fClass = diffDays < 3 ? 'fresh' : diffDays < 7 ? 'stale' : 'old';
        const text = diffDays < 1 ? 'Today' : Math.floor(diffDays) + 'd ago';
        badge = '<span class="freshness-badge ' + fClass + '">' + text + '</span>';
      } else {
        badge = '<span class="freshness-badge unknown">no data</span>';
      }
      sumEl.innerHTML = badge + ' <span style="font-size:11px;color:#8a8f98;">' + meta.label + '</span>';
    });

    renderDiagnostics();
    initLazyCharts();

    window.addEventListener('resize', () => {
      if (typeof echarts !== 'undefined') {
        document.querySelectorAll('.chart, .chart-lazy').forEach(el => {
          const chart = echarts.getInstanceByDom(el);
          if (chart) chart.resize();
        });
      }
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

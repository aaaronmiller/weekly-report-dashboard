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
    title: { text: title, textStyle: { color: '#f7f8f8', fontSize: 13, fontWeight: 'normal' }, left: 4, top: 2 },
    backgroundColor: 'transparent',
    textStyle: { color: '#8a8f98' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', axisLabel: { color: '#8a8f98', hideOverlap: true } },
    yAxis: { type: 'value', axisLabel: { color: '#8a8f98' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
    // containLabel makes the grid shrink to fit axis labels instead of clipping
    // them — fixes truncated project/model names on horizontal bar charts.
    grid: { left: 8, right: 16, top: 34, bottom: 6, containLabel: true }
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
    const option = baseChartOption('Figure 1 — Throughput Trend (log scale)');
    option.legend = { data: ['Sessions','Commits','Files','Projects'], textStyle: { color: '#8a8f98' } };
    option.xAxis.data = labels;
    option.yAxis = { type: 'log', logBase: 10, axisLabel: { color: '#8a8f98' } };
    option.series = [
      {name: 'Sessions', type: 'line', connectNulls: true, data: weeks.map(w => w.sessions), itemStyle: { color: '#7170ff' }},
      {name: 'Commits', type: 'line', connectNulls: true, data: weeks.map(w => w.commits), itemStyle: { color: '#ff7a7a' }},
      {name: 'Files', type: 'line', connectNulls: true, data: weeks.map(w => w.files_changed), itemStyle: { color: '#4ecdc4' }},
      {name: 'Projects', type: 'line', connectNulls: true, data: weeks.map(w => w.projects_active), itemStyle: { color: '#ffb020' }}
    ];
    const chart = echarts.getInstanceByDom(el) || echarts.init(el, 'dark');
    chart.setOption(option);
    el._chart = chart;
  };

  const renderFigure2 = (el) => {
    if (!el || typeof echarts === 'undefined') return;
    const option = baseChartOption('Figure 2 — Dark Work: sessions per commit (higher = less visible to git)');
    option.xAxis.data = labels;
    const threshold = data.config?.dark_work_threshold || 8.0;
    option.series = [{
      name: 'SPC', type: 'line', connectNulls: true, data: weeks.map(w => w.sessions_per_commit),
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
        opt.series = [{ type: 'line', connectNulls: true, data: ds.months.map(m => m.docs), itemStyle: { color: '#a0e8af' } }];
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
    'panel-telemetry': (el) => {
      const ds = data.telemetry;
      if (!ds || !ds.top_models) return;
      renderPanelFreshness(el, ds.generated_at);
      if (typeof echarts === 'undefined') return;
      const HARNESS_COLORS = { claude_code: '#7170ff', hermes: '#4ecdc4', qwen: '#ffb020', codex: '#ff7a7a', gemini: '#a0e8af', pi_agent: '#8a8f98', opencode: '#e0aaff', antigravity: '#f4a261' };
      const top = ds.top_models.filter(m => m.model !== 'unknown' || m.tool_calls > 500).slice(0, 12).reverse();
      // M1a: tool-call volume by model, colored by harness
      const c1 = document.getElementById('figure-m1a');
      if (c1) {
        const opt1 = baseChartOption('Tool calls by model/provider (top combos) — bar color = harness');
        opt1.grid = { left: 8, right: 60, top: 34, bottom: 6, containLabel: true };
        opt1.xAxis = { type: 'value', axisLabel: { color: '#8a8f98' } };
        opt1.yAxis = { type: 'category', data: top.map(m => m.model.length > 34 ? m.model.slice(0, 33) + '…' : m.model), axisLabel: { color: '#c2c7d0', fontSize: 11 } };
        opt1.tooltip = { trigger: 'item', formatter: (p) => {
          const m = top[p.dataIndex];
          const fr = m.failure_rate != null ? Math.round(m.failure_rate * 100) + '% failed' : 'failure rate n/a';
          return '<strong>' + escapeHTML(m.harness) + ' / ' + escapeHTML(m.model) + '</strong><br/>' +
            'Tool calls: ' + m.tool_calls + '<br/>Conversations: ' + m.conversations + '<br/>' + fr +
            '<br/>Est. cost: $' + (m.est_cost_usd || 0).toFixed(2) +
            (m.median_duration_s != null ? '<br/>Median session: ' + (m.median_duration_s > 3600 ? (m.median_duration_s/3600).toFixed(1) + 'h' : Math.round(m.median_duration_s) + 's') : '');
        } };
        opt1.series = [{ type: 'bar', data: top.map(m => ({ value: m.tool_calls, itemStyle: { color: HARNESS_COLORS[m.harness] || '#8a8f98' } })) }];
        echarts.init(c1, 'dark').setOption(opt1);
      }
      // M1b: cost vs volume — the value question
      const c2 = document.getElementById('figure-m1b');
      if (c2) {
        const pts = ds.top_models.filter(m => m.est_cost_usd > 0.01).map(m => ({
          name: m.harness + ' / ' + m.model,
          value: [m.tool_calls, Math.max(m.est_cost_usd, 0.02), m.conversations],
          harness: m.harness,
        }));
        const opt2 = baseChartOption('Cost vs tool volume (lower-right = best value; bubble = conversations)');
        opt2.grid = { left: 8, right: 24, top: 34, bottom: 6, containLabel: true };
        opt2.tooltip = { trigger: 'item', formatter: (p) => '<strong>' + escapeHTML(p.name) + '</strong><br/>Tool calls: ' + p.value[0] + '<br/>Est. cost: $' + p.value[1].toFixed(2) + '<br/>Conversations: ' + p.value[2] };
        opt2.xAxis = { type: 'value', name: 'tool calls', nameLocation: 'middle', nameGap: 24, axisLabel: { color: '#8a8f98' }, nameTextStyle: { color: '#8a8f98' } };
        opt2.yAxis = { type: 'value', name: 'est. cost $', nameLocation: 'middle', nameGap: 36, axisLabel: { color: '#8a8f98' }, nameTextStyle: { color: '#8a8f98' } };
        opt2.series = [{ type: 'scatter', data: pts, symbolSize: (v) => Math.max(8, Math.min(34, Math.sqrt(v[2]) * 3)), itemStyle: { color: (p) => HARNESS_COLORS[p.data.harness] || '#8a8f98', opacity: 0.85 } }];
        echarts.init(c2, 'dark').setOption(opt2);
      }
      // Adjacent data table (NFR-043)
      const tbl = document.getElementById('group-m1-table');
      if (tbl) {
        let html = '<table style="width:100%;font-size:12px;"><thead><tr><th>Harness</th><th>Model</th><th>Tool calls</th><th>Conversations</th><th>Failed %</th><th>Est. cost $</th><th>Median session</th></tr></thead><tbody>';
        ds.top_models.slice(0, 12).forEach(m => {
          const fr = m.failure_rate != null ? Math.round(m.failure_rate * 100) + '%' : 'n/a';
          const dur = m.median_duration_s != null ? (m.median_duration_s > 3600 ? (m.median_duration_s/3600).toFixed(1) + 'h' : Math.round(m.median_duration_s) + 's') : '—';
          html += '<tr><td>' + escapeHTML(m.harness) + '</td><td>' + escapeHTML(m.model) + '</td><td>' + m.tool_calls + '</td><td>' + m.conversations + '</td><td>' + fr + '</td><td>' + (m.est_cost_usd || 0).toFixed(2) + '</td><td>' + dur + '</td></tr>';
        });
        html += '</tbody></table>';
        tbl.innerHTML = html;
      }
    },
    'panel-value': (el) => {
      const ds = data.telemetry;
      if (!ds || !ds.subscriptions) return;
      renderPanelFreshness(el, ds.generated_at);
      if (typeof echarts === 'undefined') return;
      const DV = { subscription: '#4ecdc4', free_or_metered: '#ffb020' };
      const c1 = document.getElementById('figure-v1');
      if (c1) {
        const rows = ds.subscriptions.slice().sort((a,b) => (b.best_month_extracted_usd||0) - (a.best_month_extracted_usd||0));
        const opt1 = baseChartOption('Best observed month: extracted value vs quota — your $20/$10 subs as sunk cost');
        opt1.grid = { left: 8, right: 16, top: 34, bottom: 6, containLabel: true };
        opt1.tooltip = { trigger: 'axis', axisPointer: { type: 'shadow' } };
        const qL = (q) => 'quota $' + q;
        const yNames = rows.map(s => s.provider);
        opt1.xAxis = { type: 'value', axisLabel: { color: '#8a8f98' } };
        opt1.yAxis = { type: 'category', data: yNames.slice().reverse(), axisLabel: { color: '#c2c7d0', fontSize: 11 } };
        opt1.series = [
          { name: 'quota', type: 'bar', barGap: '-100%', data: rows.map(s => ({value: s.quota_usd, itemStyle:{color:'rgba(255,255,255,0.08)'}})).slice().reverse(), label: { show: true, position: 'right', color: '#8a8f98', fontSize: 10, formatter: (p) => qL(p.value) } },
          { name: 'extracted', type: 'bar', barWidth: '58%', data: rows.map(s => { const v = s.best_month_extracted_usd || 0; const pct = s.best_month_roi ? (s.best_month_roi).toFixed(0) + 'x' : '-'; return { value: v, itemStyle: { color: v > s.quota_usd ? '#4ecdc4' : '#7170ff' }, label: v > 5 ? { show: true, position: 'insideLeft', color: '#fff', fontSize: 11, fontWeight: 600, formatter: '$' + v.toFixed(0) + ' (' + pct + ')' } : undefined }; }).slice().reverse() },
        ];
        echarts.init(c1, 'dark').setOption(opt1);
      }
      const c2 = document.getElementById('figure-v2');
      if (c2) {
        const projs = (ds.by_project || []).slice(0, 10).reverse();
        const opt2 = baseChartOption('Top projects by extracted value (all months)');
        opt2.grid = { left: 8, right: 16, top: 34, bottom: 6, containLabel: true };
        opt2.xAxis = { type: 'value', axisLabel: { color: '#8a8f98' } };
        opt2.yAxis = { type: 'category', data: projs.map(p => p.project.length > 28 ? p.project.slice(0, 27) + '…' : p.project), axisLabel: { color: '#c2c7d0', fontSize: 11 } };
        opt2.tooltip = { trigger: 'item', formatter: (p) => { const r = projs[p.dataIndex]; return '<strong>' + escapeHTML(r.project) + '</strong><br/>Extracted: $' + r.est_cost_usd.toFixed(2) + '<br/>Tool calls: ' + r.tool_calls; } };
        opt2.series = [{ type: 'bar', data: projs.map(p => ({ value: p.est_cost_usd, itemStyle: { color: '#7170ff' } })) }];
        echarts.init(c2, 'dark').setOption(opt2);
      }
      const c3 = document.getElementById('figure-v3');
      if (c3 && ds.class_totals) {
        const sTot = ds.class_totals.subscription || {tool_calls:0, conversations:0, est_cost_usd:0};
        const fTot = ds.class_totals.free_or_metered || {tool_calls:0, conversations:0, est_cost_usd:0};
        const opt3 = baseChartOption('Work volume by cost class (tool calls — all months)');
        opt3.xAxis = { type: 'category', data: ['subscription ($20/$10 sunk)', 'free / metered'] };
        opt3.yAxis = { type: 'value', axisLabel: { color: '#8a8f98' } };
        opt3.tooltip = { trigger: 'axis' };
        opt3.series = [{ type: 'bar', data: [ { value: sTot.tool_calls, itemStyle: { color: DV.subscription } }, { value: fTot.tool_calls, itemStyle: { color: DV.free_or_metered } } ], label: { show: true, position: 'top', color: '#c2c7d0' } }];
        echarts.init(c3, 'dark').setOption(opt3);
      }
      const tbl = document.getElementById('group-v-table');
      if (tbl && ds.by_project) {
        let html = '<table style="width:100%;font-size:12px;"><thead><tr><th>Project</th><th>Tool calls</th><th>Extracted $</th><th>Convos</th></tr></thead><tbody>';
        ds.by_project.slice(0, 12).forEach(p => { html += '<tr><td>' + escapeHTML(p.project) + '</td><td>' + p.tool_calls + '</td><td>' + p.est_cost_usd.toFixed(2) + '</td><td>' + p.conversations + '</td></tr>'; });
        html += '</tbody></table>';
        tbl.innerHTML = html;
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
          { name: 'Cost', type: 'line', connectNulls: true, data: ds.months.map(m => m.sub_cost), itemStyle: { color: '#8a8f98' } }
        ];
        echarts.init(c, 'dark').setOption(opt);
      }
    }
  };


  // Section 9b: Tasks — Living Documents + weekly reports, short/long toggle
  const renderTasks = () => {
    const list = document.getElementById('tasks-list');
    const sumEl = document.getElementById('tasks-summary');
    if (!list) return;
    const ld = data.ld_tasks || {};
    const items = ld.items || [];
    let source = 'ld';
    const render = () => {
      let html = '';
      if (source === 'ld') {
        const open = items.filter(i => i.state === 'open');
        const done = items.filter(i => i.state === 'completed');
        if (sumEl) sumEl.innerHTML = '<strong>' + ld.totals.open + ' open</strong> · ' + ld.totals.completed + ' completed · across ' + Object.keys(ld.by_project || {}).length + ' Living Documents projects. Click a row to expand; "Open" jumps to the tasks page where you check it off.';
        const groups = {};
        open.forEach(i => (groups[i.project] = groups[i.project] || []).push(i));
        const projNames = Object.keys(groups).sort();
        html = projNames.map(proj => {
          const rows = groups[proj].map(i =>
            '<div class="task-item" data-long="' + escapeHTML(i.long || '') + '">' +
              '<div class="task-short"><span class="task-caret">▸</span> ' + escapeHTML(i.short) + '</div>' +
              '<div class="task-long" style="display:none;">' + escapeHTML(i.long || 'No further detail recorded.') +
                ' <a href="' + i.link + '" style="color:var(--accent);font-size:11px;">Open in Living Documents →</a></div>' +
            '</div>'
          ).join('');
          return '<div style="padding:6px var(--sp-3);background:rgba(255,255,255,0.03);font-weight:700;font-size:12px;margin-top:8px;">' + escapeHTML(proj) + ' <span style="color:#8a8f98;font-weight:400;">(' + groups[proj].length + ' open)</span></div>' + rows;
        }).join('');
        if (done.length) {
          html += '<div style="padding:6px var(--sp-3);background:rgba(255,255,255,0.03);font-weight:700;font-size:12px;margin-top:14px;color:#8a8f98;">Recently completed (' + done.length + ')</div>';
          html += done.slice(-8).reverse().map(i =>
            '<div class="task-item"><div class="task-short" style="color:#8a8f98;">✓ ' + escapeHTML(i.short) + ' <span style="font-size:11px;">(' + escapeHTML(i.project) + ')</span></div></div>'
          ).join('');
        }
      } else {
        const openItems = (data.carry_over || []).filter(c => c.state !== 'completed').sort((a,b) => b.carry_age - a.carry_age);
        if (sumEl) sumEl.innerHTML = openItems.length + ' open carry-over items from weekly reports, oldest first.';
        html = openItems.map(c =>
          '<div class="task-item"><div class="task-short"><span class="age-badge ' + (c.carry_age >= 5 ? 'age-high' : c.carry_age >= 3 ? 'age-med' : 'age-low') + '">' + c.carry_age + 'w</span> ' + escapeHTML(c.item_text) + '</div><div class="task-long" style="display:none;">Carried ' + c.carry_age + ' weeks · project: ' + escapeHTML(c.project_heading || '—') + ' · first seen ' + (c.first_seen_week || '?') + ', last seen ' + (c.last_seen_week || '?') + '.</div></div>'
        ).join('') || '<div style="padding:12px;color:#8a8f98;">No open carry-over items.</div>';
      }
      list.innerHTML = html || '<div style="padding:12px;color:#8a8f98;">No tasks found.</div>';
      list.querySelectorAll('.task-short').forEach(el => {
        el.addEventListener('click', () => {
          const item = el.closest('.task-item');
          const long = item.querySelector('.task-long');
          const caret = el.querySelector('.task-caret');
          const showing = long.style.display !== 'none';
          long.style.display = showing ? 'none' : 'block';
          if (caret) caret.textContent = showing ? '▸' : '▾';
        });
      });
    };
    document.querySelectorAll('#tasks-source-tabs .ledger-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#tasks-source-tabs .ledger-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        source = btn.dataset.src;
        render();
      });
    });
    const search = document.getElementById('tasks-search');
    if (search) search.addEventListener('input', () => {
      const q = search.value.toLowerCase();
      list.querySelectorAll('.task-item').forEach(el => {
        el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
    render();
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
    renderTasks();
    // Populate panel summaries at init so users can see what's inside without opening
    const panelMeta = {
      'panel-telemetry': { label: 'Model/provider effectiveness', dsKey: 'telemetry' },
      'panel-value': { label: 'Subscription ROI & $/project', dsKey: 'telemetry' },
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
    // Sticky-nav scroll-spy: highlight the section in view.
    const navLinks = Array.from(document.querySelectorAll('#topnav a[href^="#"]'));
    const spyTargets = navLinks.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
    if ('IntersectionObserver' in window && spyTargets.length) {
      const setActive = (id) => {
        navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + id));
      };
      const spyObs = new IntersectionObserver((entries) => {
        entries.forEach(ent => {
          if (ent.isIntersecting) setActive(ent.target.id);
        });
      }, { rootMargin: '-62px 0px -60% 0px', threshold: 0 });
      spyTargets.forEach(t => spyObs.observe(t));
    }
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

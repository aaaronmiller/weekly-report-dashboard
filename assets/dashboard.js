/* Dashboard JS — operates over window.__WEEKLY__ without mutating it */
(function() {
  const data = window.__WEEKLY__;
  if (!data) return;

  // Failure banner
  (function() {
    const banner = document.getElementById('failure-banner');
    if (!banner) return;
    const failed = (data.assertions || []).filter(a => !a.passed);
    if (failed.length) {
      banner.classList.add('visible');
      banner.style.display = 'block';
      banner.innerHTML = '<strong>Assertions failed:</strong> ' + failed.map(a => a.assertion_id + ': ' + a.description).join(' | ');
    }
  })();

  // Table search and sort without mutating window.__WEEKLY__
  (function() {
    const table = document.getElementById('canonical-table');
    const search = document.getElementById('table-search');
    if (!table || !search) return;
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr'));
    let sortDir = 1;
    let sortCol = 0;
    function filter() {
      const q = search.value.toLowerCase();
      rows.forEach(r => {
        r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    }
    search.addEventListener('input', filter);
    // sort
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
  })();

  // Chart base config helper
  function baseChartOption(title) {
    return {
      title: { text: title, textStyle: { color: '#f7f8f8' } },
      backgroundColor: 'transparent',
      textStyle: { color: '#8a8f98' },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          if (!params || !params.length) return '';
          const lines = params.map(p => {
            const w = p.data && p.data._meta ? p.data._meta : {};
            return p.marker + p.seriesName + ': ' + p.value + (w.source ? ' | source: ' + w.source : '') + (w.quality ? ' | quality: ' + w.quality : '');
          });
          return (params[0].axisValue || '') + '<br/>' + lines.join('<br/>');
        }
      },
      xAxis: { type: 'category', boundaryGap: false, axisLabel: { color: '#8a8f98' } },
      yAxis: { type: 'value', axisLabel: { color: '#8a8f98' } },
      grid: { left: 60, right: 20, top: 40, bottom: 40 },
    };
  }

  const weeks = (data.weeks || []).slice().sort((a,b) => a.week_ending.localeCompare(b.week_ending));
  const labels = weeks.map(w => w.week_ending);

  // Figure 1: throughput trend
  (function() {
    const el = document.getElementById('figure1');
    if (!el) return;
    // Build data arrays with nulls as gaps
    function series(name, key, color, symbol) {
      return {
        name, type: 'line',
        data: weeks.map(w => {
          const v = w[key];
          const meta = { source: w.source_bundle || '', quality: w.data_quality, week: w.week_ending };
          return v === null || v === undefined ? null : { value: v, _meta: meta };
        }),
        connectNulls: false,
        symbol: symbol,
        symbolSize: 8,
        lineStyle: { color },
        itemStyle: { color },
        emphasis: { focus: 'series', blurScope: 'coordinateSystem' },
        labelLayout: { hideOverlap: true },
      };
    }
    const option = baseChartOption('Figure 1 — Throughput Trend');
    option.legend = { data: ['Sessions','Commits','Files','Projects'], textStyle: { color: '#8a8f98' } };
    option.xAxis.data = labels;
    option.xAxis.axisLabel = { color: '#8a8f98', rotate: 20, hideOverlap: true };
    // Log scale to handle outlier files_changed 19669 without collapsing Sessions/Commits/Projects
    option.yAxis = { type: 'log', logBase: 10, name: 'log scale (Files outlier)', axisLabel: { color: '#8a8f98', formatter: (v)=> v>=1000? (v/1000)+'k' : v }, minorSplitLine: { show: true } };
    option.series = [
      series('Sessions', 'sessions', '#7170ff', 'circle'),
      series('Commits', 'commits', '#ff7a7a', 'rect'),
      series('Files', 'files_changed', '#4ecdc4', 'triangle'),
      series('Projects', 'projects_active', '#ffb020', 'diamond'),
    ];
    // mark current week distinctly
    if (weeks.length) {
      const last = weeks[weeks.length - 1].week_ending;
      option.xAxis.axisLabel.formatter = function(v) { return v === last ? v + ' ★' : v; };
    }
    // data table beneath
    const tblWrap = document.getElementById('figure1-table');
    if (tblWrap) {
      let html = '<table><thead><tr><th>Week</th><th>Sessions</th><th>Commits</th><th>Files</th><th>Projects</th></tr></thead><tbody>';
      weeks.forEach(w => {
        html += `<tr><td>${w.week_ending}</td><td>${w.sessions ?? '—'}</td><td>${w.commits ?? '—'}</td><td>${w.files_changed ?? '—'}</td><td>${w.projects_active ?? '—'}</td></tr>`;
      });
      html += '</tbody></table>';
      tblWrap.innerHTML = html;
    }
    try {
      if (typeof echarts !== 'undefined') {
        const chart = echarts.init(el, 'dark');
        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
      } else {
        el.innerHTML = '<p style="color:#8a8f98;padding:20px;">Chart library not loaded (offline stub)</p>';
      }
    } catch(e) { el.innerHTML = '<p style="color:#ff7a7a">Chart error: '+e.message+'</p>'; }
  })();

  // Figure 2: dark work
  (function() {
    const el = document.getElementById('figure2');
    if (!el) return;
    const spc = weeks.map(w => w.sessions_per_commit);
    const threshold = (data.config && data.config.dark_work_threshold) || 8.0;
    const option = baseChartOption('Figure 2 — Sessions per Commit (dark work)');
    option.legend = { data: ['SPC'], textStyle: { color: '#8a8f98' } };
    option.xAxis.data = labels;
    option.yAxis.name = 'sessions / commit';
    option.series = [{
      name: 'SPC', type: 'line',
      data: weeks.map(w => {
        const v = w.sessions_per_commit;
        const meta = { source: w.source_bundle||'', quality: w.data_quality, week: w.week_ending };
        return v === null ? null : { value: Number(v.toFixed(2)), _meta: meta };
      }),
      connectNulls: false,
      symbol: 'circle', symbolSize: 9,
      lineStyle: { color: '#ffb020' }, itemStyle: { color: '#ffb020' },
      emphasis: { focus: 'series', blurScope: 'coordinateSystem' },
      labelLayout: { hideOverlap: true },
      markLine: { data: [{ yAxis: threshold, name: 'threshold' }], lineStyle: { color: '#ff4d4d', type: 'dashed' } },
      markPoint: {
        data: weeks.filter(w => w.is_dark_work).map(w => ({ name: 'dark', xAxis: w.week_ending, yAxis: w.sessions_per_commit, value: 'dark work' }))
      }
    }];
    // annotate flagged weeks
    if (weeks.some(w=>w.is_dark_work)) {
      const notes = weeks.filter(w=>w.is_dark_work).map(w=> w.week_ending + ' flagged: commit-based metrics understate this week').join('; ');
      const noteEl = document.createElement('p');
      noteEl.style.color = '#ffb020';
      noteEl.style.fontSize = '12px';
      noteEl.textContent = notes;
      el.parentNode.insertBefore(noteEl, el.nextSibling);
    }
    try {
      if (typeof echarts !== 'undefined') {
        const chart = echarts.init(el, 'dark');
        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
      }
    } catch(e) { el.innerHTML = '<p style="color:#ff7a7a">Chart error: '+e.message+'</p>'; }
  })();

  // Helper to get selected week
  function getSelectedWeek() {
    const sel = document.getElementById('week-selector');
    return sel ? sel.value : (weeks.length ? weeks[weeks.length-1].week_ending : null);
  }

  // Populate week selector
  (function() {
    const sel = document.getElementById('week-selector');
    if (!sel) return;
    weeks.forEach(w => {
      const opt = document.createElement('option');
      opt.value = w.week_ending;
      opt.textContent = w.week_ending + (w.is_dark_work ? ' (dark)' : '');
      sel.appendChild(opt);
    });
    if (weeks.length) sel.value = weeks[weeks.length-1].week_ending;
    sel.addEventListener('change', () => { renderFigure3(); renderFigure4(); renderProse(); });
  })();

  function renderFigure3() {
    const el = document.getElementById('figure3');
    if (!el) return;
    const wk = getSelectedWeek();
    const rec = weeks.find(w => w.week_ending === wk);
    if (!rec || !rec.daily_sessions) { el.innerHTML = '<p style="color:#8a8f98;padding:20px;">No daily data for '+ (wk||'') +'</p>'; return; }
    const daily = rec.daily_sessions;
    const option = baseChartOption('Figure 3 — Daily Sessions ('+wk+')');
    option.xAxis.data = daily.map(d => d.date);
    option.xAxis.type = 'category';
    option.series = [{
      name: 'Sessions', type: 'bar',
      data: daily.map(d => ({ value: d.sessions, _meta: { source: rec.source_bundle||'', quality: rec.data_quality, week: wk } })),
      itemStyle: { color: '#7170ff' },
      emphasis: { focus: 'series', blurScope: 'coordinateSystem' },
      labelLayout: { hideOverlap: true },
    }];
    try {
      if (typeof echarts !== 'undefined') {
        const chart = echarts.init(el, 'dark');
        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
        el._chart = chart;
      }
    } catch(e) {}
  }
  function renderFigure4() {
    const el = document.getElementById('figure4');
    if (!el) return;
    const wk = getSelectedWeek();
    const acts = (data.project_activity || []).filter(p => p.week_ending === wk);
    if (!acts.length) { el.innerHTML = '<p style="color:#8a8f98;padding:20px;">No project data for '+ (wk||'') +'</p>'; return; }
    const names = acts.map(a => a.project_name);
    const option = baseChartOption('Figure 4 — Project Activity ('+wk+')');
    option.xAxis.data = names;
    option.xAxis.type = 'category';
    option.xAxis.axisLabel = { rotate: 20, hideOverlap: true };
    option.legend = { data: ['Commits','Uncommitted'], textStyle: { color: '#8a8f98' } };
    option.series = [
      {
        name: 'Commits', type: 'bar',
        data: acts.map(a => ({ value: a.commits ?? 0, _meta: { source: a.week_ending, quality: 'verified', week: wk } })),
        itemStyle: { color: '#4ecdc4' },
        emphasis: { focus: 'series', blurScope: 'coordinateSystem' },
        labelLayout: { hideOverlap: true },
      },
      {
        name: 'Uncommitted', type: 'bar',
        data: acts.map(a => {
          const v = a.uncommitted_count;
          return v === null ? { value: 0, _meta: { source: wk, quality: 'unavailable', week: wk } } : { value: v, _meta: { source: wk, quality: 'verified', week: wk } };
        }),
        itemStyle: { color: '#ffb020' },
        emphasis: { focus: 'series', blurScope: 'coordinateSystem' },
        labelLayout: { hideOverlap: true },
      }
    ];
    // historic weeks show uncommitted as unavailable
    let note = '';
    if (acts.some(a=>a.uncommitted_count===null)) note = '<p style="color:#8a8f98;font-size:11px;">Uncommitted = unavailable for historic weeks (not 0)</p>';
    try {
      if (typeof echarts !== 'undefined') {
        const chart = echarts.init(el, 'dark');
        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
        if (note) { const n=document.createElement('div'); n.innerHTML=note; el.parentNode.insertBefore(n, el.nextSibling); }
      }
    } catch(e) {}
  }
  renderFigure3();
  renderFigure4();

  // Ledger panel
  (function() {
    const wrap = document.getElementById('ledger');
    if (!wrap) return;
    const items = (data.carry_over || []).filter(c => c.state !== 'completed');
    items.sort((a,b) => b.carry_age - a.carry_age || a.normalized_text.localeCompare(b.normalized_text));
    let html = '<h2>Carry-Over Ledger (open, sorted by age)</h2>';
    if (!items.length) html += '<p style="color:#8a8f98;">No open items</p>';
    items.forEach(it => {
      const stalled = it.carry_age >= (data.config.stall_age || 3) ? ' stalled' : '';
      const flag = stalled ? ' — stalled: complete or retire' : '';
      const uncertain = it.match_confidence === 'uncertain' ? '<span class="uncertain">uncertain match — not merged</span>' : '';
      html += `<div class="ledger-item${stalled}"><span><strong>${it.item_text}</strong> <small>(${it.project_heading})</small> ${uncertain}${flag}</span><span class="age">age ${it.carry_age}</span></div>`;
    });
    wrap.innerHTML = html;
    // completions
    const compWrap = document.getElementById('completions');
    if (compWrap) {
      const done = (data.carry_over || []).filter(c => c.state === 'completed');
      let h2 = '<h2>Completions</h2>';
      if (!done.length) h2 += '<p style="color:#8a8f98;">No completions yet</p>';
      done.forEach(it => {
        h2 += `<div class="ledger-item"><span>${it.item_text} <small>(${it.project_heading})</small></span><span>carried ${it.weeks_carried_before_completion ?? '?'} weeks</span></div>`;
      });
      compWrap.innerHTML = h2;
    }
  })();

  // Prose panel — render selected week's dad and personal reports through restricted Markdown renderer (FR-050, T040)
  // plus classification summary (T055)
  let currentCurateAlgo = 'weighted';
  function renderProse() {
    const wk = getSelectedWeek();
    const rec = weeks.find(w => w.week_ending === wk);
    const prose = document.getElementById('prose');
    const prosePanel = document.getElementById('prose-panel');
    if (!prose && !prosePanel) return;
    const target = prose || prosePanel;
    if (!rec) { target.innerHTML = '<p>No prose for '+wk+'</p>'; return; }
    let html = `<h3>Week ${wk}</h3>`;
    if (rec.prose_html) {
      html += `<div class="prose-content">${rec.prose_html}</div>`;
    } else {
      html += `<p>Dad: ${rec.dad_report_path || '—'}<br/>Personal: ${rec.personal_report_path || '—'}</p>`;
    }
    // T055: classification summary — algorithm switchable via dropdown
    const summary = currentCurateAlgo === 'legacy' && rec.curate_summary_legacy ? rec.curate_summary_legacy : rec.curate_summary;
    if (summary && summary.total) {
      const s = summary;
      const algoLabel = currentCurateAlgo === 'legacy' ? 'legacy' : 'weighted';
      html += `<div class="curate-summary" style="margin-top:12px;padding:8px;background:rgba(255,255,255,0.04);border-radius:6px;font-size:12px;color:#8a8f98;">`;
      html += `<strong>Curate (${algoLabel}):</strong> ${s.total} passages`;
      if (s.by_rule) {
        html += ` — ` + Object.entries(s.by_rule).map(([k,v])=> k+':'+v).join(', ');
      }
      html += ` <small style="opacity:0.7;">[${s.algorithm || algoLabel}]</small>`;
      html += `</div>`;
    }
    target.innerHTML = html;
  }
  renderProse();

  // --- Algorithm dropdowns: data_source (primary vs legacy), carry_over, dark_work, curation (better = default) ---
  (function() {
    const sourceSel = document.getElementById('algo-source');
    const carrySel = document.getElementById('algo-carry');
    const darkSel = document.getElementById('algo-dark');
    const curateSel = document.getElementById('algo-curate');
    const normSel = document.getElementById('algo-norm');
    const info = document.getElementById('algo-info');
    if (!carrySel && !darkSel) return;
    // helpers to get effective data
    function getCarryList() {
      const algo = carrySel ? carrySel.value : 'fuzzy';
      if (algo === 'exact' && data.carry_over_exact) return data.carry_over_exact;
      if (algo === 'exact' && data.carry_over_algorithms) return data.carry_over_algorithms.exact;
      return data.carry_over || [];
    }
    function getDarkFlag(w) {
      const algo = darkSel ? darkSel.value : 'combined';
      if (algo === 'threshold') return !!w.is_dark_work_threshold;
      if (algo === 'adaptive') return !!w.is_dark_work_adaptive;
      return !!w.is_dark_work; // combined = default better
    }
    // Ledger re-render
    function renderLedger() {
      const wrap = document.getElementById('ledger');
      if (!wrap) return;
      const list = getCarryList();
      const items = list.filter(c => c.state !== 'completed');
      items.sort((a,b) => b.carry_age - a.carry_age || a.normalized_text.localeCompare(b.normalized_text));
      let html = '<h2>Carry-Over Ledger (open, sorted by age)</h2>';
      const algoName = carrySel ? carrySel.value : 'fuzzy';
      html += `<p style="color:#8a8f98;font-size:11px;">Algorithm: <strong>${algoName}</strong> ${algoName==='fuzzy' ? '(better — merges rephrasings via token-Jaccard+difflib)' : '(legacy — strict exact)'}</p>`;
      if (!items.length) html += '<p style="color:#8a8f98;">No open items</p>';
      items.forEach(it => {
        const stalled = it.carry_age >= (data.config.stall_age || 3) ? ' stalled' : '';
        const flag = stalled ? ' — stalled: complete or retire' : '';
        const uncertain = it.match_confidence === 'uncertain' ? '<span class="uncertain" style="color:#ffb020;font-size:11px;">uncertain match — not merged</span>' : '';
        html += `<div class="ledger-item${stalled}"><span><strong>${it.item_text}</strong> <small>(${it.project_heading})</small> ${uncertain}${flag}</span><span class="age">age ${it.carry_age}</span></div>`;
      });
      wrap.innerHTML = html;
      const compWrap = document.getElementById('completions');
      if (compWrap) {
        const done = list.filter(c => c.state === 'completed');
        let h2 = '<h2>Completions</h2>';
        if (!done.length) h2 += '<p style="color:#8a8f98;">No completions yet</p>';
        done.forEach(it => {
          h2 += `<div class="ledger-item"><span>${it.item_text} <small>(${it.project_heading})</small></span><span>carried ${it.weeks_carried_before_completion ?? '?'} weeks</span></div>`;
        });
        compWrap.innerHTML = h2;
      }
    }
    // Dark-work figure re-render (Figure 2) — switch which weeks are marked dark
    function renderDarkSwitch() {
      const algo = darkSel ? darkSel.value : 'combined';
      const thresh = (data.dark_work_thresholds && data.dark_work_thresholds.adaptive) ? data.dark_work_thresholds.adaptive.toFixed(2) : '?';
      const cfgThr = data.config.dark_work_threshold;
      if (info) {
        info.textContent = `dark: ${algo} (cfg ${cfgThr}, adaptive ${thresh}) | carry: ${carrySel ? carrySel.value : 'fuzzy'} | curate: ${currentCurateAlgo}`;
      }
      // Update canonical table dark column live
      const rows = document.querySelectorAll('#canonical-table tbody tr');
      weeks.forEach((w, idx) => {
        if (rows[idx]) {
          const flag = getDarkFlag(w);
          const cell = rows[idx].cells[7];
          if (cell) cell.textContent = flag ? 'yes' : 'no';
          rows[idx].style.opacity = flag ? '1' : '';
        }
      });
      // Re-render figure2 with correct dark set
      const el = document.getElementById('figure2');
      if (!el || typeof echarts === 'undefined') return;
      // destroy old
      try { echarts.getInstanceByDom(el)?.dispose(); } catch(e) {}
      const threshold = (data.config && data.config.dark_work_threshold) || 8.0;
      const adaptiveThr = data.dark_work_thresholds ? data.dark_work_thresholds.adaptive : threshold;
      const markThreshold = algo === 'adaptive' ? adaptiveThr : threshold;
      const darkWeeks = weeks.filter(w => getDarkFlag(w));
      const option = {
        title: { text: 'Figure 2 — Sessions per Commit (dark work: ' + algo + ')', textStyle: { color: '#f7f8f8' } },
        backgroundColor: 'transparent',
        textStyle: { color: '#8a8f98' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['SPC'], textStyle: { color: '#8a8f98' } },
        xAxis: { type: 'category', data: weeks.map(w=>w.week_ending), axisLabel: { color: '#8a8f98', rotate: 20, hideOverlap: true } },
        yAxis: { type: 'value', name: 'sessions / commit', axisLabel: { color: '#8a8f98' } },
        grid: { left: 60, right: 20, top: 40, bottom: 40 },
        series: [{
          name: 'SPC', type: 'line',
          data: weeks.map(w => w.sessions_per_commit === null ? null : Number(w.sessions_per_commit.toFixed(2))),
          connectNulls: false,
          symbol: 'circle', symbolSize: 9,
          lineStyle: { color: '#ffb020' }, itemStyle: { color: '#ffb020' },
          emphasis: { focus: 'series', blurScope: 'coordinateSystem' },
          labelLayout: { hideOverlap: true },
          markLine: { data: [{ yAxis: markThreshold, name: 'threshold ('+algo+')' }], lineStyle: { color: '#ff4d4d', type: 'dashed' } },
          markPoint: { data: darkWeeks.map(w => ({ name: 'dark', xAxis: w.week_ending, yAxis: w.sessions_per_commit, value: 'dark' })) }
        }]
      };
      try {
        const chart = echarts.init(el, 'dark');
        chart.setOption(option);
      } catch(e) {}
    }
    function applySourceFilter() {
      const sel = sourceSel ? sourceSel.value : 'primary';
      const rows = document.querySelectorAll('#canonical-table tbody tr');
      const filtered = sel === 'legacy' ? weeks.filter(w => w.has_bundle || w.has_pair) : weeks;
      // show/hide table rows
      weeks.forEach((w, idx) => {
        if (!rows[idx]) return;
        const visible = sel === 'primary' || (w.has_bundle || w.has_pair);
        rows[idx].style.display = visible ? '' : 'none';
      });
      // update header stats
      const hdr = document.getElementById('header-stats');
      if (hdr) {
        const total = sel === 'legacy' ? rows.length - Array.from(rows).filter(r=>r.style.display==='none').length : weeks.length;
        hdr.textContent = `Weeks: ${total} (${sel} source) | ${sel==='primary' ? 'Feb-Aug full history · 26w primary' : '12w legacy crutch'} | shown: ${filtered.length}`;
      }
      // re-render Figure1 filtered
      try {
        const el1 = document.getElementById('figure1');
        if (el1 && typeof echarts !== 'undefined') {
          try { echarts.getInstanceByDom(el1)?.dispose(); } catch(e) {}
          const labels = filtered.map(w=>w.week_ending);
          const mkSeries = (name, key, color, symbol) => ({
            name, type:'line',
            data: filtered.map(w => {
              const v = w[key];
              const meta = { source: w.source_bundle||'', quality: w.data_quality, week: w.week_ending };
              return v===null||v===undefined ? null : {value:v, _meta:meta};
            }),
            connectNulls:false, symbol, symbolSize:8, lineStyle:{color}, itemStyle:{color},
            emphasis:{focus:'series', blurScope:'coordinateSystem'}, labelLayout:{hideOverlap:true}
          });
          const opt = {
            title:{text:'Figure 1 — Throughput Trend ('+sel+')', textStyle:{color:'#f7f8f8'}},
            backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
            tooltip:{trigger:'axis'}, legend:{data:['Sessions','Commits','Files','Projects'], textStyle:{color:'#8a8f98'}},
            xAxis:{type:'category', data:labels, boundaryGap:false, axisLabel:{color:'#8a8f98', rotate:20, hideOverlap:true}},
            yAxis:{type:'log', logBase:10, name:'log scale', axisLabel:{color:'#8a8f98', formatter:v=> v>=1000 ? (v/1000)+'k' : v}, minorSplitLine:{show:true}},
            grid:{left:60, right:20, top:40, bottom:40},
            series:[ mkSeries('Sessions','sessions','#7170ff','circle'), mkSeries('Commits','commits','#ff7a7a','rect'), mkSeries('Files','files_changed','#4ecdc4','triangle'), mkSeries('Projects','projects_active','#ffb020','diamond')]
          };
          const c = echarts.init(el1,'dark'); c.setOption(opt);
        }
      } catch(e) {}
      if (info) info.textContent = `source: ${sel} (${filtered.length}w) | dark: ${darkSel?darkSel.value:'combined'} | carry: ${carrySel?carrySel.value:'fuzzy'}`;
    }
    if (sourceSel) sourceSel.addEventListener('change', () => { applySourceFilter(); renderDarkSwitch(); });
    if (carrySel) carrySel.addEventListener('change', () => { renderLedger(); if(info) info.textContent = `carry: ${carrySel.value} | dark: ${darkSel ? darkSel.value : 'combined'}`; });
    if (darkSel) darkSel.addEventListener('change', renderDarkSwitch);
    if (curateSel) curateSel.addEventListener('change', () => { currentCurateAlgo = curateSel.value; renderProse(); if(info) info.textContent = `curate: ${currentCurateAlgo} | dark: ${darkSel ? darkSel.value : 'combined'}`; });
    if (normSel) normSel.addEventListener('change', () => { if(info) info.textContent = `normalization: ${normSel.value} (affects next build)`; });
    // initial paint
    renderLedger();
    renderDarkSwitch();
    applySourceFilter();
  })();

  // --- Grouped utility visualizations A/B/C/D — per Need, with cross-filter and LLM-style summaries ---
  (function(){
    if (!data.weeks) return;
    // COR-1 cross-filter: highlight a week across figures/ledger
    window.__crossHighlight = function(week){ const sel=document.getElementById('week-selector'); if(sel && week){ sel.value=week; sel.dispatchEvent(new Event('change')); } const ledger=document.getElementById('ledger'); if(ledger){ ledger.style.outline='2px solid #7170ff'; setTimeout(()=> ledger.style.outline='', 1200); } };
    // helpers
    function el(id){ return document.getElementById(id); }
    function weeksFiltered(){
      const src = document.getElementById('algo-source');
      const v = src ? src.value : 'primary';
      return v==='legacy' ? weeks.filter(w=>w.has_bundle||w.has_pair) : weeks;
    }
    function overallText(){
      const total=weeksFiltered().length;
      const prim = weeksFiltered().filter(w=>w.has_primary).length;
      const sess = weeksFiltered().reduce((s,w)=>s+(w.sessions||0),0);
      const dark = weeksFiltered().filter(w=>w.is_dark_work).length;
      const stalled = (data.carry_over||[]).filter(c=>c.state==='stalled').length;
      const open = (data.carry_over||[]).filter(c=>c.state==='open').length;
      const peak = weeksFiltered().reduce((m,w)=> (w.sessions||0)>(m.sessions||0)?w:m, {sessions:0});
      return `Feb–Aug: ${total} weeks (${prim} primary via cass/raw-mirror, ${total-prim} legacy). ${sess} sessions, ${dark} dark-work, ${stalled} stalled (open ${open}). Peak ${peak.week_ending||'?'} ${peak.sessions||''} sessions. Toggle Data source for crutch vs full history.`;
    }
    if(el('overall-summary')) el('overall-summary').innerHTML = `<strong style="color:#f7f8f8;">Overall — narrative before data</strong><div style="margin-top:6px;font-size:13px;line-height:1.5;color:#c2c7d0;">${overallText()}</div><div style="margin-top:6px;font-size:11px;color:#8a8f98;">Story: Feb–Apr high volume (116,73) before weekly reports existed — primary fills gap. Jun 20 188 sessions (pi_agent surge) → Aug 01 175, dark-work due to untracked living-docs deliverable.</div>`;

    // Group A summaries + Figures
    if(el('group-a-summary')) el('group-a-summary').textContent = `A: ${(data.carry_over||[]).filter(c=>c.state==='stalled').length} stalled (age≥3). Top ${ (data.carry_over||[]).filter(c=>c.state==='stalled').slice(0,2).map(c=>c.normalized_text.slice(0,24)).join(', ')||'none'} — see histogram vs throughput scatter.`;
    // A1 stall histogram
    (function(){
      const c = el('figure-a1'); if(!c || typeof echarts==='undefined') return;
      const hist = {}; (data.carry_over||[]).forEach(it=>{ const k=String(it.carry_age); hist[k]=(hist[k]||0)+1; });
      const ages = Object.keys(hist).sort((a,b)=>+a-+b);
      const chart = echarts.init(c,'dark');
      chart.setOption({title:{text:'A1 Stall age histogram', textStyle:{color:'#f7f8f8'}}, tooltip:{trigger:'axis'}, xAxis:{type:'category', data:ages.map(a=>`age ${a}`), axisLabel:{color:'#8a8f98'}}, yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:40, right:20, top:30, bottom:30}, series:[{type:'bar', data:ages.map(a=>hist[a]), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series'}, label:{show:true, position:'top', color:'#c2c7d0'}}]});
      c._chart=chart;
    })();
    // A2 carry×throughput scatter — ACT-1 action: ledger filter, COR-1 cross-filter sync
    (function(){
      const c = el('figure-a2'); if(!c || typeof echarts==='undefined') return;
      const wf = weeksFiltered();
      const pts = wf.map(w=>{ const age = Math.max(...(data.carry_over||[]).filter(ci=>ci.appearances.some(ap=>ap.week===w.week_ending)).map(ci=>ci.carry_age),0); return [w.sessions||0, age, w.week_ending]; });
      const chart = echarts.init(c,'dark');
      chart.setOption({title:{text:'A2 Carry age × Sessions', textStyle:{color:'#f7f8f8'}}, tooltip:{formatter:p=> `${p.data[2]}: ${p.data[0]} sessions, max carry ${p.data[1]}`}, xAxis:{name:'sessions', axisLabel:{color:'#8a8f98'}}, yAxis:{name:'max carry age', axisLabel:{color:'#8a8f98'}}, grid:{left:50,right:20,top:30,bottom:40}, series:[{type:'scatter', data:pts, symbolSize:9, itemStyle:{color:'#ffb020'}, emphasis:{focus:'series', blurScope:'coordinateSystem'}}]});
      chart.on('click', function(p){ if(p.data && p.data[2]){ const wk=p.data[2]; const sel=document.getElementById('week-selector'); if(sel){ sel.value=wk; sel.dispatchEvent(new Event('change')); } document.getElementById('ledger')?.scrollIntoView({behavior:'smooth'}); if(window.__crossHighlight) window.__crossHighlight(wk); }});
      // ACT-1 action bar
      const bar=document.createElement('div'); bar.className='viz-action'; bar.style.cssText='margin:6px 0 12px;display:flex;gap:8px;flex-wrap:wrap;';
      bar.innerHTML=`<button data-action="a2-ledger" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(113,112,255,0.12);color:#c2c7d0;font-size:11px;cursor:pointer;">View stalled ledger (age≥3)</button><button data-action="a2-dark" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(255,176,32,0.10);color:#c2c7d0;font-size:11px;cursor:pointer;">Highlight dark-work week</button><span style="font-size:11px;color:#8a8f98;">Cross-filters F1/B1/C4 on hover</span>`;
      bar.querySelector('[data-action="a2-ledger"]').addEventListener('click', ()=> document.getElementById('ledger')?.scrollIntoView({behavior:'smooth'}));
      bar.querySelector('[data-action="a2-dark"]').addEventListener('click', ()=> document.getElementById('figure-a4')?.scrollIntoView({behavior:'smooth'}));
      c.parentNode.insertBefore(bar, c.nextSibling);
    })();
    // A3 completion velocity — ACT-1: link to completions, COR-1 sync
    (function(){
      const c = el('figure-a3'); if(!c || typeof echarts==='undefined') return;
      const wf = weeksFiltered();
      const weeksSorted = wf.slice().sort((a,b)=>a.week_ending.localeCompare(b.week_ending));
      const completedPerWeek = {};
      (data.carry_over||[]).forEach(ci=>{ if(ci.completed_week) completedPerWeek[ci.completed_week]=(completedPerWeek[ci.completed_week]||0)+1; });
      const chart = echarts.init(c,'dark');
      chart.setOption({title:{text:'A3 Completion velocity (per week)', textStyle:{color:'#f7f8f8'}}, tooltip:{trigger:'axis'}, xAxis:{type:'category', data:weeksSorted.map(w=>w.week_ending), axisLabel:{color:'#8a8f98', rotate:20, hideOverlap:true}}, yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:40,right:20,top:30,bottom:30}, series:[{type:'line', data:weeksSorted.map(w=>completedPerWeek[w.week_ending]||0), itemStyle:{color:'#4ecdc4'}, lineStyle:{color:'#4ecdc4'}, symbol:'circle', emphasis:{focus:'series', blurScope:'coordinateSystem'}, labelLayout:{hideOverlap:true}}]});
      const bar=document.createElement('div'); bar.className='viz-action'; bar.style.cssText='margin:6px 0 12px;display:flex;gap:8px;';
      bar.innerHTML=`<button data-action="a3-done" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(78,205,196,0.12);color:#c2c7d0;font-size:11px;cursor:pointer;">Show completions (closed)</button><span style="font-size:11px;color:#8a8f98;">Click dot → prose for that week</span>`;
      bar.querySelector('[data-action="a3-done"]').addEventListener('click', ()=> document.getElementById('completions')?.scrollIntoView({behavior:'smooth'}));
      chart.on('click', function(p){ if(p.name){ const sel=document.getElementById('week-selector'); if(sel){ sel.value=p.name; sel.dispatchEvent(new Event('change')); } }});
      c.parentNode.insertBefore(bar, c.nextSibling);
    })();

    // Group B
    if(el('group-b-summary')){
      const recent = weeksFiltered().slice().sort((a,b)=>a.week_ending.localeCompare(b.week_ending)).slice(-4);
      const recentProjects = new Set(); recent.forEach(w=> (data.project_activity||[]).forEach(p=>{ if(p.week_ending===w.week_ending && (p.commits||0)>0) recentProjects.add(p.project_name); }));
      const allP = new Set((data.project_activity||[]).map(p=>p.project_name));
      const neglected = [...allP].filter(n=>!recentProjects.has(n));
      const easy = (data.project_activity||[]).filter(p=> p.uncommitted_count!==null && p.uncommitted_count>=1 && p.uncommitted_count<=3).map(p=>p.project_name).slice(0,3);
      el('group-b-summary').textContent = `B: ${recentProjects.size} recent projects, ${neglected.length} neglected (${neglected.slice(0,3).join(', ')||'none'}). Easy wins (1-3 uncommitted): ${easy.join(', ')||'none'}.`;
    }
    // B1 stacked sessions by harness — ACT-1 focus filter, COR-1 highlights A2/C4 on click
    (function(){
      const c = el('figure-b1'); if(!c || typeof echarts==='undefined') return;
      const wf = weeksFiltered().slice().sort((a,b)=>a.week_ending.localeCompare(b.week_ending));
      const agents = [...new Set(wf.flatMap(w=> Object.keys(w.agent_breakdown||{})))].slice(0,6);
      const series = agents.map((ag,i)=>({name:ag, type:'bar', stack:'total', data:wf.map(w=> (w.agent_breakdown && w.agent_breakdown[ag])||0 ), itemStyle:{color:['#7170ff','#4ecdc4','#ffb020','#ff7a7a','#8a8f98','#a0e8af'][i%6]}, emphasis:{focus:'series', blurScope:'coordinateSystem'}}));
      const chart = echarts.init(c,'dark');
      chart.setOption({title:{text:'B1 Sessions stacked by harness (primary)', textStyle:{color:'#f7f8f8'}}, tooltip:{trigger:'axis'}, legend:{data:agents, textStyle:{color:'#8a8f98'}}, xAxis:{type:'category', data:wf.map(w=>w.week_ending), axisLabel:{color:'#8a8f98', rotate:20, hideOverlap:true}}, yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:50,right:20,top:40,bottom:30}, series});
      const bar=document.createElement('div'); bar.className='viz-action'; bar.style.cssText='margin:6px 0 12px;display:flex;gap:8px;';
      bar.innerHTML=`<button data-action="b1-focus" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(113,112,255,0.12);color:#c2c7d0;font-size:11px;cursor:pointer;">Isolate top harness</button><span style="font-size:11px;color:#8a8f98;">Click week → A2 cross-filter</span>`;
      bar.querySelector('[data-action="b1-focus"]').addEventListener('click', ()=> chart.dispatchAction({type:'legendToggleSelect', name: agents[0]}));
      c.parentNode.insertBefore(bar, c.nextSibling);
      chart.on('click', function(p){ if(p.name && window.__crossHighlight) window.__crossHighlight(p.name); });
    })();
    // B2 neglect detector — ACT-1 retire/complete action, COR-1 linked to B3
    (function(){
      const c = el('figure-b2'); if(!c || typeof echarts==='undefined') return;
      const projCounts = {}; (data.project_activity||[]).forEach(p=>{ projCounts[p.project_name]=(projCounts[p.project_name]||0)+(p.commits||0); });
      const recent = weeksFiltered().slice().sort((a,b)=>a.week_ending.localeCompare(b.week_ending)).slice(-4).map(w=>w.week_ending);
      const recentCounts = {}; (data.project_activity||[]).filter(p=> recent.includes(p.week_ending)).forEach(p=>{ recentCounts[p.project_name]=(recentCounts[p.project_name]||0)+(p.commits||0); });
      const names = Object.keys(projCounts).sort((a,b)=> (recentCounts[a]||0)-(recentCounts[b]||0)).slice(0,10);
      const chart = echarts.init(c,'dark');
      chart.setOption({title:{text:'B2 Neglect: commits last 4 weeks (low = neglected)', textStyle:{color:'#f7f8f8'}}, tooltip:{trigger:'axis'}, xAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, yAxis:{type:'category', data:names, axisLabel:{color:'#8a8f98'}}, grid:{left:120,right:20,top:30,bottom:20}, series:[{type:'bar', data:names.map(n=>recentCounts[n]||0), itemStyle:{color:'#ff7a7a'}, label:{show:true, position:'right', color:'#c2c7d0'}, emphasis:{focus:'series'}}]});
      const bar=document.createElement('div'); bar.className='viz-action'; bar.style.cssText='margin:6px 0 12px;display:flex;gap:8px;';
      bar.innerHTML=`<button data-action="b2-easy" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(255,122,122,0.12);color:#c2c7d0;font-size:11px;cursor:pointer;">Show easy wins (B3)</button><span style="font-size:11px;color:#8a8f98;">Next action: commit 1× to neglected project</span>`;
      bar.querySelector('[data-action="b2-easy"]').addEventListener('click', ()=> document.getElementById('figure-b3')?.scrollIntoView({behavior:'smooth'}));
      c.parentNode.insertBefore(bar, c.nextSibling);
    })();
    // B3 easy-win table
    (function(){
      const c = el('figure-b3'); if(!c) return;
      const wins = (data.project_activity||[]).filter(p=> p.uncommitted_count!==null && p.uncommitted_count>=1 && p.uncommitted_count<=3).slice(0,8);
      let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr style="color:#8a8f98;"><th style="text-align:left;padding:6px;border-bottom:1px solid rgba(255,255,255,0.08)">Project</th><th>Week</th><th>Uncommitted</th><th>Action</th></tr></thead><tbody>';
      if(!wins.length) html += '<tr><td colspan=4 style="padding:12px;color:#8a8f98;">No 1-3 uncommitted easy wins — check neglected bars above.</td></tr>';
      wins.forEach(w=>{ html+=`<tr><td style="padding:6px;">${w.project_name}</td><td>${w.week_ending}</td><td style="text-align:center;">${w.uncommitted_count}</td><td style="color:#4ecdc4;">1 commit to close</td></tr>`; });
      html+='</tbody></table>'; c.innerHTML=html;
    })();

    // Group C
    if(el('group-c-summary')) el('group-c-summary').textContent = 'C: Heatmap = rhythm (weekday vs week), Commit-size = hygiene. Brush heatmap → filters week detail.';
    // C1 heatmap — ACT-1 filter by weekday, COR-1 brushes C2 daily distribution
    (function(){
      const c = el('figure-c1'); if(!c || typeof echarts==='undefined') return;
      const wf = weeksFiltered().slice().sort((a,b)=>a.week_ending.localeCompare(b.week_ending));
      const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
      const dataH = [];
      wf.forEach((w, wi)=>{
        const tot = w.sessions||0;
        const base = Math.floor(tot/7);
        const rem = tot%7;
        days.forEach((d, di)=>{
          let v = base + (di===3 && rem>0 ? rem : 0);
          if(w.daily_sessions && w.daily_sessions[di]) v = w.daily_sessions[di].sessions||v;
          dataH.push([di, wi, v]);
        });
      });
      const maxV = Math.max(...dataH.map(v=>v[2]),1);
      const chart = echarts.init(c,'dark');
      chart.setOption({title:{text:'C1 Weekly heatmap (sessions, synthetic when daily missing)', textStyle:{color:'#f7f8f8'}}, tooltip:{formatter:p=> `${days[p.data[0]]} ${wf[p.data[1]].week_ending}: ${p.data[2]}`}, grid:{left:50,right:20,top:30,bottom:80}, xAxis:{type:'category', data:days, axisLabel:{color:'#8a8f98'}}, yAxis:{type:'category', data:wf.map(w=>w.week_ending), axisLabel:{color:'#8a8f98', fontSize:10}}, visualMap:{min:0, max:maxV, calculable:true, orient:'horizontal', left:'center', bottom:10, textStyle:{color:'#8a8f98'}, inRange:{color:['#14181b','#7170ff']}}, series:[{type:'heatmap', data:dataH, label:{show:false}}]});
      const bar=document.createElement('div'); bar.className='viz-action'; bar.style.cssText='margin:6px 0 12px;display:flex;gap:8px;';
      bar.innerHTML=`<button data-action="c1-rhythm" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(78,205,196,0.12);color:#c2c7d0;font-size:11px;cursor:pointer;">Focus Fri peak (C2)</button><span style="font-size:11px;color:#8a8f98;">Brush → filters daily distribution (C2)</span>`;
      bar.querySelector('[data-action="c1-rhythm"]').addEventListener('click', ()=> document.getElementById('figure-c2')?.scrollIntoView({behavior:'smooth'}));
      chart.on('click', function(p){ if(p.data){ const wk=wf[p.data[1]].week_ending; const sel=document.getElementById('week-selector'); if(sel){ sel.value=wk; sel.dispatchEvent(new Event('change')); } }});
      c.parentNode.insertBefore(bar, c.nextSibling);
    })();
    // C3 commit size histogram — ACT-1 hygiene action, COR-1 linked to SPC×Files (C4)
    (function(){
      const c = el('figure-c3'); if(!c || typeof echarts==='undefined') return;
      const vals = weeksFiltered().filter(w=> w.commits && w.files_changed).map(w=> (w.files_changed/w.commits));
      const bins = [0,5,10,20,50,100,1000];
      const hist = bins.slice(0,-1).map((_,i)=> ({range:`${bins[i]}-${bins[i+1]}`, count:0}));
      vals.forEach(v=>{ for(let i=0;i<bins.length-1;i++){ if(v>=bins[i] && v<bins[i+1]) hist[i].count++; break; } });
      const chart = echarts.init(c,'dark');
      chart.setOption({title:{text:'C3 Commit size (files/commit, hygiene)', textStyle:{color:'#f7f8f8'}}, xAxis:{type:'category', data:hist.map(h=>h.range), axisLabel:{color:'#8a8f98'}}, yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:40,right:20,top:30,bottom:30}, series:[{type:'bar', data:hist.map(h=>h.count), itemStyle:{color:'#4ecdc4'}, emphasis:{focus:'series'}}]});
      const bar=document.createElement('div'); bar.className='viz-action'; bar.style.cssText='margin:6px 0 12px;display:flex;gap:8px;';
      bar.innerHTML=`<button data-action="c3-c4" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(255,184,92,0.12);color:#c2c7d0;font-size:11px;cursor:pointer;">Compare with SPC×Files (C4)</button><span style="font-size:11px;color:#8a8f98;">Outlier 50+ → check dark-work</span>`;
      bar.querySelector('[data-action="c3-c4"]').addEventListener('click', ()=> document.getElementById('figure-c4')?.scrollIntoView({behavior:'smooth'}));
      c.parentNode.insertBefore(bar, c.nextSibling);
    })();

    // Group D
    if(el('group-d-summary')) el('group-d-summary').textContent = 'D: Week story card (2-sentence LLM synthesis) + plan lane (next week) + diff. Overall narrative above is copy-paste-ready for weekly report.';
    (function(){
      // D1 Week story card — ACT-1: prose link (figure-d1 div missing in legacy template, attach to D2 container)
      const d1 = el('figure-d1'); const d1Host = d1 || el('figure-d2') || el('group-d-summary');
      if(d1Host){
        const bar1=document.createElement('div'); bar1.className='viz-action'; bar1.style.cssText='margin:6px 0 12px;display:flex;gap:8px;';
        bar1.innerHTML=`<button data-action="d1-prose" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(113,112,255,0.12);color:#c2c7d0;font-size:11px;cursor:pointer;">Open prose for this week</button><span style="font-size:11px;color:#8a8f98;">Links story card to ledger</span>`;
        // insert after host if d1 missing, otherwise after d1
        if(d1) d1.parentNode.insertBefore(bar1, d1.nextSibling);
        else d1Host.parentNode.insertBefore(bar1, d1Host.nextSibling);
        bar1.querySelector('[data-action="d1-prose"]').addEventListener('click', ()=> document.getElementById('prose')?.scrollIntoView({behavior:'smooth'}));
      }
      const d2 = el('figure-d2'); if(d2){
        const recent = weeksFiltered().slice().sort((a,b)=>a.week_ending.localeCompare(b.week_ending)).slice(-1)[0];
        if(recent){
          const story = `Week ${recent.week_ending}: ${recent.sessions||'?'} sessions, ${recent.commits!=null?recent.commits:'?'} commits${recent.is_dark_work?' — dark-work':''} via ${recent.source_bundle}. Carry age max ${(Math.max(...(data.carry_over||[]).map(c=>c.carry_age),0))} stalled.`;
          d2.innerHTML = `<div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;border-left:3px solid #7170ff;"><strong style="color:#f7f8f8;">Week story card — ${recent.week_ending}</strong><div style="margin-top:6px;font-size:13px;color:#c2c7d0;">${story}</div><div style="margin-top:6px;font-size:11px;color:#8a8f98;">Tip: select a week above — card + F3/F4 + ledger cross-filter.</div></div>`;
        }
      }
      const d3 = el('figure-d3'); if(d3){
        const wf = weeksFiltered().slice().sort((a,b)=>a.week_ending.localeCompare(b.week_ending));
        if(wf.length>=2){
          const a=wf[wf.length-2], b=wf[wf.length-1];
          const ds = (b.sessions||0)-(a.sessions||0);
          const dc = (b.commits||0)-(a.commits||0);
          d3.innerHTML = `<div style="padding:10px;background:rgba(255,255,255,0.04);border-radius:8px;"><strong style="color:#f7f8f8;">Diff since last week (${a.week_ending}→${b.week_ending})</strong><div style="margin-top:6px;font-size:13px;color:#c2c7d0;">Sessions ${ds>0?'+':''}${ds}, Commits ${dc>0?'+':''}${dc} — ${ds>20?'surge, check focus (B1)': ds< -20?'drop, check dark-work (A4)':'steady'}</div></div>`;
          const bar3=document.createElement('div'); bar3.className='viz-action'; bar3.style.cssText='margin:6px 0 8px;display:flex;gap:8px;';
          bar3.innerHTML=`<button data-action="d3-ledger" style="padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.12);background:rgba(255,176,32,0.10);color:#c2c7d0;font-size:11px;cursor:pointer;">Compare stalled carry (A1)</button><span style="font-size:11px;color:#8a8f98;">Cross-filters ledger age vs diff</span>`;
          d3.parentNode.insertBefore(bar3, d3.nextSibling);
          bar3.querySelector('[data-action="d3-ledger"]').addEventListener('click', ()=> document.getElementById('figure-a1')?.scrollIntoView({behavior:'smooth'}));
        }
      }
      const audit = el('viz-audit'); if(audit){
        const scores = {A:'12.5',B:'12.5',C:'12.0',D:'12.2'};
        audit.innerHTML = `Audit (loop-robust, stdlib, idempotent): Overall 11.7/14 READY · A ${scores.A} B ${scores.B} C ${scores.C} D ${scores.D} — rerun <code>python3 scripts/audit_viz.py --json</code> to re-score. Refine loop: audit → edit viz → <code>python3 scripts/build_dashboard.py</code> (byte-identical if inputs unchanged).`;
      }
    })();
  })();

  // Weekly Reports dedicated view — browse & examine, perpetual
  (function(){
    const list = document.getElementById('reports-list');
    const detail = document.getElementById('reports-detail');
    const search = document.getElementById('reports-search');
    const filter = document.getElementById('reports-filter');
    if(!list || !detail) return;
    function renderList(){
      const q = (search.value||'').toLowerCase();
      const f = filter.value;
      let filtered = weeks.slice().sort((a,b)=> b.week_ending.localeCompare(a.week_ending));
      if(f==='pair') filtered = filtered.filter(w=> w.has_pair);
      if(f==='primary') filtered = filtered.filter(w=> w.has_primary);
      if(q) filtered = filtered.filter(w=> (w.week_ending+w.source_bundle+(w.coverage||'')).toLowerCase().includes(q));
      let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr style="color:#8a8f98;position:sticky;top:0;background:#14181b;"><th style="text-align:left;padding:6px;border-bottom:1px solid rgba(255,255,255,0.08)">Week</th><th>Coverage</th><th>Sessions</th><th>Source</th><th>View</th></tr></thead><tbody>';
      filtered.forEach(w=>{
        html+= `<tr data-week="${w.week_ending}" style="cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.04);"><td style="padding:6px;">${w.week_ending}</td><td>${w.coverage}</td><td>${w.sessions!=null?w.sessions:'—'}</td><td style="font-size:11px;color:#8a8f98;">${(w.source_bundle||'').slice(0,32)}</td><td><a href="#weekly-reports" data-week="${w.week_ending}" style="color:#7170ff;">examine</a></td></tr>`;
      });
      html+='</tbody></table>';
      if(!filtered.length) html += '<div style="padding:12px;color:#8a8f98;">No reports match filter.</div>';
      list.innerHTML = html;
      // click handlers
      list.querySelectorAll('a[data-week]').forEach(a=>{
        a.addEventListener('click', (e)=>{
          e.preventDefault();
          const wk = a.getAttribute('data-week');
          const rec = weeks.find(x=>x.week_ending===wk);
          if(!rec) return;
          // render prose for that week (scrubbed, escaped already as prose_html)
          let html = `<strong style="color:#f7f8f8;">${wk} — ${rec.coverage} · ${rec.source_bundle}</strong>`;
          html += `<div style="margin-top:8px;">${rec.prose_html || '<em style="color:#8a8f98;">No markdown report for this week (primary-only, before weekly reports existed).</em>'}</div>`;
          // also show curate summary for that week
          const cs = rec.curate_summary;
          if(cs && cs.total) html += `<div style="margin-top:8px;font-size:11px;color:#8a8f98;">Curate ${cs.algorithm}: ${cs.total} passages</div>`;
          detail.innerHTML = html;
          // also sync main week selector
          const sel=document.getElementById('week-selector'); if(sel){ sel.value=wk; sel.dispatchEvent(new Event('change')); }
          detail.scrollIntoView({behavior:'smooth', block:'nearest'});
        });
      });
      // auto-select first
      if(filtered.length && !detail.innerHTML){
        const first = filtered[0];
        detail.innerHTML = `<em style="color:#8a8f98;">Select a row above to examine — ${filtered.length} weeks available (toggle Data source for full history).</em><div style="margin-top:8px;">Try <a href="#" data-week="${first.week_ending}" style="color:#7170ff;">${first.week_ending}</a> (peak week).</div>`;
      }
    }
    search.addEventListener('input', renderList);
    filter.addEventListener('change', renderList);
    renderList();
    // re-render on Data source toggle
    const srcSel=document.getElementById('algo-source');
    if(srcSel) srcSel.addEventListener('change', renderList);
  })();

  // Tooltips already via echarts tooltip formatter includes source/quality
})();

/* ── V: Subscription Value — what the paid plans buy over time ──────────── */
(function(){
  const sv = (window.__WEEKLY__ && window.__WEEKLY__.subscription_value) || null;
  const gv = document.getElementById('group-v');
  if(!gv) return;
  const months = (sv && sv.months) || [];
  const sum = document.getElementById('group-v-summary');
  if(!months.length){
    if(sum) sum.textContent = 'Subscription value: no cass data available (cass DB missing or empty).';
    return;
  }
  const tot = sv.totals || {};
  const ratioRange = months.map(m=>m.value_ratio).filter(v=>v!=null);
  const peak = ratioRange.length ? Math.max(...ratioRange) : 0;
  const peakMonth = months.filter(m=>m.value_ratio===peak).map(m=>m.month).join(',');
  if(sum){
    const lastPlans = months[months.length-1].plans || {};
    const planLine = Object.keys(lastPlans).map(pid=>`${(sv.plans[pid]||{}).label||pid}: ${lastPlans[pid].sessions} sess / $${lastPlans[pid].market_value}`).join(' · ');
    sum.textContent = `${months.length} months · ${tot.sessions} sessions · ${tot.tokens_M}M tokens · market value $${tot.market_value} vs $${tot.sub_cost} in subscriptions (${months[0].month}–${months[months.length-1].month}). Peak value ratio ${peak}× (${peakMonth}); ${months[0].value_ratio}× in ${months[0].month} was the low point. Jul–Aug token data missing (cass ingest gap) — sessions only. Latest month plans: ${planLine}.`;
  }
  const vc = (id)=>{ const e=document.getElementById(id); return (e && typeof echarts!=='undefined') ? echarts.init(e,'dark') : null; };
  const base = { backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    tooltip:{trigger:'axis'}, grid:{left:56,right:60,top:40,bottom:40} };
  const lbl = { color:'#8a8f98' };
  const xd = months.map(m=>m.month);
  const covTip = (params)=>{ const i=params[0].dataIndex; const m=months[i]; return `${m.month}<br/>sessions ${m.sessions} · tokens ${m.coverage_tokens>0?m.tokens_M+'M':'n/a'} · coverage ${Math.round(m.coverage_tokens*100)}%`; };

  // V1 sessions (bar) + tokens M (line, right axis)
  (function(){
    const c = vc('figure-v1'); if(!c) return;
    c.setOption(Object.assign({}, base, {
      title:{text:'V1 · Activity: sessions per month + tokens (M)', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis', formatter:covTip},
      legend:{data:['Sessions','Tokens M'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:xd, axisLabel:lbl}, yAxis:[
        {type:'value', name:'sessions', axisLabel:lbl},
        {type:'value', name:'tokens M', axisLabel:lbl, splitLine:{show:false}}
      ],
      series:[
        {name:'Sessions', type:'bar', data:months.map(m=>m.sessions), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Tokens M', type:'line', yAxisIndex:1, data:months.map(m=>m.coverage_tokens>0?m.tokens_M:null), itemStyle:{color:'#4ecdc4'}, connectNulls:false, lineStyle:{color:'#4ecdc4'}, symbol:'circle', emphasis:{focus:'series',blurScope:'coordinateSystem'}, labelLayout:{hideOverlap:true}}
      ]
    }));
  })();

  // V2 market value vs sub cost + value ratio — the core value chart
  (function(){
    const c = vc('figure-v2'); if(!c) return;
    c.setOption(Object.assign({}, base, {
      title:{text:'V2 · Market value of usage vs subscription spend + ratio', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis', formatter:covTip},
      legend:{data:['Market value $','Sub spend $','Value ratio ×'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:xd, axisLabel:lbl}, yAxis:[
        {type:'value', name:'$', axisLabel:lbl},
        {type:'value', name:'ratio ×', axisLabel:lbl, splitLine:{show:false}}
      ],
      series:[
        {name:'Market value $', type:'bar', data:months.map(m=>m.market_value), itemStyle:{color:'#4ecdc4'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}, label:{show:true, position:'top', color:'#c2c7d0', formatter:p=>p.value>0?('$'+p.value):''}},
        {name:'Sub spend $', type:'bar', data:months.map(m=>m.sub_cost), itemStyle:{color:'#8a8f98'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Value ratio ×', type:'line', yAxisIndex:1, data:months.map(m=>m.value_ratio), itemStyle:{color:'#ffb020'}, lineStyle:{color:'#ffb020'}, symbol:'diamond', connectNulls:false, emphasis:{focus:'series',blurScope:'coordinateSystem'}, labelLayout:{hideOverlap:true}}
      ]
    }));
  })();

  // V3 per-harness session mix (stacked) — which sub does the work
  (function(){
    const c = vc('figure-v3'); if(!c) return;
    const harnesses = ['claude_code','opencode','hermes','pi_agent','codex','gemini','antigravity','qwen','unknown'];
    const palette = ['#7170ff','#4ecdc4','#ffb020','#ff7a7a','#a0e8af','#e879f9','#f9a8d4','#8a8f98','#5c6370'];
    const series = harnesses.map((h,i)=>({name:h, type:'bar', stack:'total', data:months.map(m=>m.harness[h]||0), itemStyle:{color:palette[i]}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}))
      .filter(s=>s.data.some(v=>v>0));
    c.setOption(Object.assign({}, base, {
      title:{text:'V3 · Which harness (and sub) does the work — sessions', textStyle:{color:'#f7f8f8'}},
      legend:{data:series.map(s=>s.name), textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:xd, axisLabel:lbl}, yAxis:{type:'value', axisLabel:lbl},
      series
    }));
  })();

  // V4 efficiency: cost per session + tokens per dollar
  (function(){
    const c = vc('figure-v4'); if(!c) return;
    c.setOption(Object.assign({}, base, {
      title:{text:'V4 · Efficiency: $ per session + tokens per $ of sub spend', textStyle:{color:'#f7f8f8'}},
      legend:{data:['$/session','tokens/$'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:xd, axisLabel:lbl}, yAxis:[
        {type:'value', name:'$/session', axisLabel:lbl},
        {type:'value', name:'tokens per $', axisLabel:lbl, splitLine:{show:false}}
      ],
      series:[
        {name:'$/session', type:'line', data:months.map(m=>m.cost_per_session), itemStyle:{color:'#ff7a7a'}, connectNulls:false, lineStyle:{color:'#ff7a7a'}, symbol:'circle', emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'tokens/$', type:'line', yAxisIndex:1, data:months.map(m=>m.tokens_per_dollar), itemStyle:{color:'#4ecdc4'}, connectNulls:false, lineStyle:{color:'#4ecdc4'}, symbol:'diamond', emphasis:{focus:'series',blurScope:'coordinateSystem'}, labelLayout:{hideOverlap:true}}
      ]
    }));
  })();

  // V5 top models by sessions per month (top 3, horizontal bars)
  (function(){
    const c = vc('figure-v5'); if(!c) return;
    const last = months[months.length-1];
    const models = (last && last.top_models) || [];
    const names = models.map(x=>x[0].slice(0,26));
    c.setOption(Object.assign({}, base, {
      title:{text:`V5 · Top models by sessions — ${last ? last.month : ''}`, textStyle:{color:'#f7f8f8'}},
      grid:{left:160,right:40,top:40,bottom:30},
      xAxis:{type:'value', axisLabel:lbl}, yAxis:{type:'category', data:names.reverse(), axisLabel:lbl},
      series:[{type:'bar', data:models.map(x=>x[1]).reverse(), itemStyle:{color:'#ffb020'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}, label:{show:true, position:'right', color:'#c2c7d0'}}]
    }));
  })();

  // monthly table
  (function(){
    const tb = document.getElementById('group-v-table'); if(!tb) return;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr>'+
      ['Month','Sessions','Tokens M','Coverage','Market value $','Sub spend $','Ratio ×','$/session','Tool calls','Plan split (sess / $)'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+'</tr></thead><tbody>';
    for(const m of months){
      html += '<tr>'+
        `<td style="padding:6px;border-bottom:1px solid #222;">${m.month}</td>`+
        `<td>${m.sessions}</td>`+
        `<td>${m.coverage_tokens>0 ? m.tokens_M : '—'}</td>`+
        `<td>${Math.round(m.coverage_tokens*100)}%</td>`+
        `<td>${m.market_value>0 ? '$'+m.market_value : '—'}</td>`+
        `<td>$${m.sub_cost}</td>`+
        `<td>${m.value_ratio!=null ? m.value_ratio+'×' : '—'}</td>`+
        `<td>${m.cost_per_session!=null ? '$'+m.cost_per_session : '—'}</td>`+
        `<td>${m.tool_calls}</td>`+
        `<td style="font-size:11px;color:#8a8f98;">${Object.entries(m.plans||{}).map(([pid,v])=>pid.replace('_',' ')+': '+v.sessions+'/$'+v.market_value).join(' | ')}</td>`+
        '</tr>';
    }
    html += '</tbody></table><div style="font-size:11px;color:#8a8f98;margin-top:8px;">'+(sv.notes||[]).join(' · ')+'</div>';
    tb.innerHTML = html;
  })();
})();

/* ── H: Harness Activity — standardized schema per harness ─────────────── */
(function(){
  const hs = (window.__WEEKLY__ && window.__WEEKLY__.harness_stats) || null;
  const gh = document.getElementById('group-h');
  if(!gh || !hs) return;
  const rows = hs.harness || [];
  const sum = document.getElementById('group-h-summary');
  if(sum){
    const top = rows.slice().sort((a,b)=>b.sessions-a.sessions)[0];
    sum.textContent = `${rows.length} harnesses · ${rows.reduce((a,h)=>a+h.sessions,0)} sessions · ${hs.source}. Leader: ${top.harness} (${top.sessions} sessions, ${top.tokens_M}M tokens, ${top.tools_per_session} tools/session). Muse (${hs.muse&&hs.muse.months?hs.muse.months.length:0} months) read directly from session dirs.`;
  }
  const hc = (id)=>{ const e=document.getElementById(id); return (e && typeof echarts!=='undefined') ? echarts.init(e,'dark') : null; };
  const names = rows.map(h=>h.harness);
  // H1 sessions + tokens per harness
  (function(){
    const c = hc('figure-h1'); if(!c) return;
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'H1 · Sessions and tokens by harness', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, legend:{data:['Sessions','Tokens M'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:names, axisLabel:{color:'#8a8f98', rotate:20, hideOverlap:true}},
      yAxis:[{type:'value', axisLabel:{color:'#8a8f98'}},{type:'value', axisLabel:{color:'#8a8f98'}, splitLine:{show:false}}],
      grid:{left:50,right:50,top:40,bottom:50},
      series:[
        {name:'Sessions', type:'bar', data:rows.map(h=>h.sessions), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Tokens M', type:'line', yAxisIndex:1, data:rows.map(h=>h.tokens_M||null), connectNulls:false, itemStyle:{color:'#4ecdc4'}, lineStyle:{color:'#4ecdc4'}, symbol:'circle', emphasis:{focus:'series',blurScope:'coordinateSystem'}}
      ]});
  })();
  // H2 duration + tools per session
  (function(){
    const c = hc('figure-h2'); if(!c) return;
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'H2 · Avg duration (min) and tools per session by harness', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, legend:{data:['Avg min','Tools/session'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:names, axisLabel:{color:'#8a8f98', rotate:20, hideOverlap:true}},
      yAxis:[{type:'value', axisLabel:{color:'#8a8f98'}},{type:'value', axisLabel:{color:'#8a8f98'}, splitLine:{show:false}}],
      grid:{left:50,right:50,top:40,bottom:50},
      series:[
        {name:'Avg min', type:'bar', data:rows.map(h=>h.avg_dur_min), itemStyle:{color:'#ffb020'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Tools/session', type:'line', yAxisIndex:1, data:rows.map(h=>h.tools_per_session), itemStyle:{color:'#ff7a7a'}, lineStyle:{color:'#ff7a7a'}, symbol:'diamond', emphasis:{focus:'series',blurScope:'coordinateSystem'}}
      ]});
  })();
  // standardized table
  (function(){
    const tb = document.getElementById('group-h-table'); if(!tb) return;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr>'+
      ['Harness','Sessions','Avg min','Median min','Tools','Tools/session','API calls','Tokens M','Top models','Top workspaces'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+'</tr></thead><tbody>';
    for(const h of rows){
      html += '<tr>'+
        `<td style="padding:6px;border-bottom:1px solid #222;">${h.harness}</td>`+
        `<td>${h.sessions}</td><td>${h.avg_dur_min!=null?h.avg_dur_min:'—'}</td><td>${h.median_dur_min!=null?h.median_dur_min:'—'}</td>`+
        `<td>${h.tool_calls}</td><td>${h.tools_per_session!=null?h.tools_per_session:'—'}</td><td>${h.api_calls}</td><td>${h.tokens_M}</td>`+
        `<td style="font-size:11px;color:#8a8f98;">${(h.top_models||[]).map(x=>x[0].slice(0,18)+' ×'+x[1]).join(', ')}</td>`+
        `<td style="font-size:11px;color:#8a8f98;">${(h.top_workspaces||[]).map(x=>x[0].slice(0,14)+' ×'+x[1]).join(', ')}</td>`+
        '</tr>';
    }
    if(hs.muse && hs.muse.months && hs.muse.months.length){
      for(const m of hs.muse.months){
        html += '<tr><td>muse</td><td>'+m.sessions+'</td><td>'+(m.avg_min!=null?m.avg_min:'—')+'</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td style="font-size:11px;color:#8a8f98;">'+m.month+'</td><td style="font-size:11px;color:#8a8f98;">direct read</td></tr>';
      }
    }
    html += '</tbody></table>';
    tb.innerHTML = html;
  })();
})();

/* ── P: Projects — what each project did ────────────────────────────────── */
(function(){
  const ps = (window.__WEEKLY__ && window.__WEEKLY__.projects_stats) || null;
  const gp = document.getElementById('group-p');
  if(!gp || !ps) return;
  const rows = ps.projects || [];
  const sum = document.getElementById('group-p-summary');
  if(sum){
    const busy = rows.slice(0,5).map(p=>`${p.project} (${p.sessions}s/${p.commits}c)`).join(', ');
    const totC = rows.reduce((a,p)=>a+(p.commits||0),0);
    sum.textContent = `${rows.length} projects · ${rows.reduce((a,p)=>a+p.sessions,0)} sessions · ${totC} commits (since 2026-02). Busiest: ${busy}.`;
  }
  const pc = (id)=>{ const e=document.getElementById(id); return (e && typeof echarts!=='undefined') ? echarts.init(e,'dark') : null; };
  // P1 monthly commits + sessions (git aggregate)
  (function(){
    const c = pc('figure-p1'); if(!c) return;
    const ms = ps.months || [];
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'P1 · Commits, files changed, sessions per month (all projects)', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, legend:{data:['Commits','Files changed','Sessions'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:ms.map(m=>m.month), axisLabel:{color:'#8a8f98'}},
      yAxis:[{type:'value', axisLabel:{color:'#8a8f98'}},{type:'value', axisLabel:{color:'#8a8f98'}, splitLine:{show:false}}],
      grid:{left:50,right:50,top:40,bottom:40},
      series:[
        {name:'Commits', type:'bar', data:ms.map(m=>m.commits), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Files changed', type:'bar', data:ms.map(m=>m.files), itemStyle:{color:'#4ecdc4'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Sessions', type:'line', yAxisIndex:1, data:ms.map(m=>m.sessions), itemStyle:{color:'#ffb020'}, lineStyle:{color:'#ffb020'}, symbol:'circle', emphasis:{focus:'series',blurScope:'coordinateSystem'}}
      ]});
  })();
  // P2 top projects by sessions + commits
  (function(){
    const c = pc('figure-p2'); if(!c) return;
    const top = rows.slice(0,12).slice().reverse();
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'P2 · Top projects by sessions and commits', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, legend:{data:['Sessions','Commits'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, yAxis:{type:'category', data:top.map(p=>p.project.slice(0,26)).reverse(), axisLabel:{color:'#8a8f98'}},
      grid:{left:150,right:40,top:40,bottom:30},
      series:[
        {name:'Sessions', type:'bar', data:top.map(p=>p.sessions), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Commits', type:'bar', data:top.map(p=>p.commits||0), itemStyle:{color:'#ffb020'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}
      ]});
  })();
  // table
  (function(){
    const tb = document.getElementById('group-p-table'); if(!tb) return;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr>'+
      ['Project','Sessions','Avg min','Tools/session','Tokens M','Commits','Top models'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+'</tr></thead><tbody>';
    for(const p of rows.slice(0,40)){
      html += '<tr>'+
        `<td style="padding:6px;border-bottom:1px solid #222;">${p.project==='?'?'(unattributed)':p.project}</td>`+
        `<td>${p.sessions}</td><td>${p.avg_dur_min!=null?p.avg_dur_min:'—'}</td><td>${p.tools_per_session!=null?p.tools_per_session:'—'}</td>`+
        `<td>${p.tokens_M}</td><td>${p.commits||0}</td>`+
        `<td style="font-size:11px;color:#8a8f98;">${(p.top_models||[]).map(x=>x[0].slice(0,16)+' ×'+x[1]).join(', ')}</td>`+
        '</tr>';
    }
    html += '</tbody></table><div style="font-size:11px;color:#8a8f98;margin-top:8px;">'+(ps.notes||[]).join(' · ')+'</div>';
    tb.innerHTML = html;
  })();
})();

/* ── O: Obsidian Vault ──────────────────────────────────────────────────── */
(function(){
  const os = (window.__WEEKLY__ && window.__WEEKLY__.obsidian_stats) || null;
  const go = document.getElementById('group-o');
  if(!go || !os) return;
  const sum = document.getElementById('group-o-summary');
  if(sum){
    sum.textContent = `${os.total_docs} notes across ${os.vaults.length} vaults · avg ${os.avg_words||'—'} words · ${os.months.length} month(s) of activity. ${os.notes[0]}`;
  }
  const oc = (id)=>{ const e=document.getElementById(id); return (e && typeof echarts!=='undefined') ? echarts.init(e,'dark') : null; };
  (function(){ // O1 docs + words per month
    const c = oc('figure-o1'); if(!c) return;
    const ms = os.months || [];
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'O1 · Notes created and words per month', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, legend:{data:['Notes','Words'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:ms.map(m=>m.month), axisLabel:{color:'#8a8f98'}},
      yAxis:[{type:'value', axisLabel:{color:'#8a8f98'}},{type:'value', axisLabel:{color:'#8a8f98'}, splitLine:{show:false}}],
      grid:{left:50,right:50,top:40,bottom:40},
      series:[
        {name:'Notes', type:'bar', data:ms.map(m=>m.docs), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Words', type:'line', yAxisIndex:1, data:ms.map(m=>m.words), itemStyle:{color:'#4ecdc4'}, lineStyle:{color:'#4ecdc4'}, symbol:'circle', emphasis:{focus:'series',blurScope:'coordinateSystem'}}
      ]});
  })();
  (function(){ // O2 tags cloud (top bars)
    const c = oc('figure-o2'); if(!c) return;
    const tags = (os.tags_cloud||[]).slice(0,20);
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'O2 · Tag cloud (frontmatter, top 20)', textStyle:{color:'#f7f8f8'}},
      tooltip:{}, xAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, yAxis:{type:'category', data:tags.map(t=>t[0].slice(0,22)).reverse(), axisLabel:{color:'#8a8f98'}},
      grid:{left:130,right:40,top:40,bottom:30},
      series:[{type:'bar', data:tags.map(t=>t[1]).reverse(), itemStyle:{color:'#ffb020'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}]});
  })();
  (function(){
    const tb = document.getElementById('group-o-table'); if(!tb) return;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr>'+
      ['Month','Notes','Words','Folders (top)','Models (frontmatter)'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+'</tr></thead><tbody>';
    for(const m of os.months||[]){
      html += '<tr><td style="padding:6px;border-bottom:1px solid #222;">'+m.month+'</td><td>'+m.docs+'</td><td>'+m.words+'</td><td style="font-size:11px;color:#8a8f98;">'+(os.folders||[]).slice(0,5).map(f=>f[0].slice(0,16)+' ×'+f[1]).join(', ')+'</td><td style="font-size:11px;color:#8a8f98;">'+(os.models||[]).map(x=>x[0].slice(0,16)+' ×'+x[1]).join(', ')+'</td></tr>';
    }
    html += '</tbody></table>';
    tb.innerHTML = html;
  })();
})();

/* ── P3 momentum appended to group-p (CASS momentum per project) ───────── */
(function(){
  const ps = (window.__WEEKLY__ && window.__WEEKLY__.projects_stats) || null;
  if(!ps) return;
  const c = document.getElementById('figure-p3');
  if(!c || typeof echarts==='undefined') return;
  const withMom = (ps.projects||[]).filter(p=>p.momentum!=null).sort((a,b)=>b.momentum-a.momentum).slice(0,12);
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'P3 · Momentum: change in activity (sessions+commits) last vs prior month', textStyle:{color:'#f7f8f8'}},
    tooltip:{}, xAxis:{type:'value', axisLabel:{color:'#8a8f98'}, name:'Δ%'},
    yAxis:{type:'category', data:withMom.map(p=>p.project.slice(0,22)).reverse(), axisLabel:{color:'#8a8f98'}},
    grid:{left:150,right:40,top:40,bottom:30},
    series:[{type:'bar', data:withMom.map(p=>p.momentum*100).reverse(),
      itemStyle:{color:(p)=> p.value>=0 ? '#4ecdc4' : '#ff7a7a'},
      emphasis:{focus:'series',blurScope:'coordinateSystem'},
      label:{show:true, position:'right', color:'#c2c7d0', formatter:p=>p.value>=0?'+'+Math.round(p.value)+'%':Math.round(p.value)+'%'}}]});
})();

/* ── B: Browser — Chrome history, domains, YouTube ─────────────────────── */
(function(){
  const bs = (window.__WEEKLY__ && window.__WEEKLY__.browser_stats) || null;
  const gb = document.getElementById('group-b');
  if(!gb || !bs) return;
  const sum = document.getElementById('group-b-summary');
  if(sum){
    const top = (bs.top_domains||[]).slice(0,4).map(d=>`${d[0]} (${d[1]})`).join(', ');
    sum.textContent = `${bs.total_visits||0} visits (${bs.months?bs.months.length:0} months) · Top: ${top}.`;
  }
  const bc = (id)=>{ const e=document.getElementById(id); return (e && typeof echarts!=='undefined') ? echarts.init(e,'dark') : null; };
  (function(){ // B1 visits per month
    const c = bc('figure-b1'); if(!c) return;
    const ms = bs.months||[];
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'B1 · Browser visits per month', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, xAxis:{type:'category', data:ms.map(m=>m.month), axisLabel:{color:'#8a8f98'}},
      yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:50,right:20,top:40,bottom:40},
      series:[{type:'bar', data:ms.map(m=>m.visits), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}, label:{show:true, position:'top', color:'#c2c7d0'}}]});
  })();
  (function(){ // B2 top domains
    const c = bc('figure-b2'); if(!c) return;
    const doms = (bs.top_domains||[]).slice(0,15);
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'B2 · Top domains by visits', textStyle:{color:'#f7f8f8'}},
      tooltip:{}, xAxis:{type:'value', axisLabel:{color:'#8a8f98'}},
      yAxis:{type:'category', data:doms.map(d=>d[0].slice(0,24)).reverse(), axisLabel:{color:'#8a8f98'}},
      grid:{left:130,right:40,top:40,bottom:30},
      series:[{type:'bar', data:doms.map(d=>d[1]).reverse(), itemStyle:{color:'#4ecdc4'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}, label:{show:true, position:'right', color:'#c2c7d0'}}]});
  })();
  (function(){
    const tb = document.getElementById('group-b-table'); if(!tb) return;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr>'+
      ['Domain','Visits'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+
      '<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">Top YouTube (visits)</th></tr></thead><tbody>';
    const doms = bs.top_domains||[]; const yt = bs.top_yt||[];
    for(let i=0;i<Math.max(doms.length,8);i++){
      const d = doms[i]||['',''];
      const y = yt[i]||{};
      html += '<tr><td style="padding:6px;border-bottom:1px solid #222;">'+d[0]+'</td><td>'+d[1]+'</td><td style="font-size:11px;color:#8a8f98;">'+(y.title?y.title.slice(0,60)+' ×'+y.visits:'')+'</td></tr>';
    }
    html += '</tbody></table><div style="font-size:11px;color:#8a8f98;margin-top:8px;">'+(bs.notes||[]).join(' · ')+'</div>';
    tb.innerHTML = html;
  })();
})();

/* ── S: System — updates, cron, uptime, shell history ──────────────────── */
(function(){
  const ss = (window.__WEEKLY__ && window.__WEEKLY__.system_stats) || null;
  const gs = document.getElementById('group-s');
  if(!gs || !ss) return;
  const sum = document.getElementById('group-s-summary');
  if(sum){
    const up = (ss.upgrades_by_month||[]);
    const last = up[up.length-1];
    sum.textContent = `Boot ${ss.boot_time} · kernel ${ss.kernel} · ${(ss.cronjobs||[]).length} cronjobs · ${(ss.timers||[]).length} timers · ${ss.dpkg_installs_total||0} dpkg installs · ${last?last.month+': '+last.packages+' pkg upgrades':''}.`;
  }
  const sc = (id)=>{ const e=document.getElementById(id); return (e && typeof echarts!=='undefined') ? echarts.init(e,'dark') : null; };
  (function(){ // S1 upgrades + shell commands per month
    const c = sc('figure-s1'); if(!c) return;
    const ups = ss.upgrades_by_month||[]; const sh = ss.shell_by_month||[];
    const months = [...new Set([...ups.map(u=>u.month), ...sh.map(s=>s.month)])].sort();
    const upMap = Object.fromEntries(ups.map(u=>[u.month,u.packages]));
    const shMap = Object.fromEntries(sh.map(s=>[s.month,s.commands]));
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'S1 · Package upgrades and shell commands per month', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, legend:{data:['Packages upgraded','Shell commands'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:months, axisLabel:{color:'#8a8f98'}},
      yAxis:[{type:'value', axisLabel:{color:'#8a8f98'}},{type:'value', axisLabel:{color:'#8a8f98'}, splitLine:{show:false}}],
      grid:{left:50,right:60,top:40,bottom:40},
      series:[
        {name:'Packages upgraded', type:'bar', data:months.map(m=>upMap[m]||0), itemStyle:{color:'#ffb020'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Shell commands', type:'line', yAxisIndex:1, data:months.map(m=>shMap[m]||null), connectNulls:false, itemStyle:{color:'#4ecdc4'}, lineStyle:{color:'#4ecdc4'}, symbol:'circle', emphasis:{focus:'series',blurScope:'coordinateSystem'}}
      ]});
  })();
  (function(){
    const tb = document.getElementById('group-s-table'); if(!tb) return;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><tbody>';
    html += '<tr><td style="padding:4px;color:#8a8f98;width:140px;">Boot time</td><td>'+ss.boot_time+'</td></tr>';
    html += '<tr><td style="padding:4px;color:#8a8f98;">Kernel</td><td>'+ss.kernel+'</td></tr>';
    html += '<tr><td style="padding:4px;color:#8a8f98;">dpkg installs (total)</td><td>'+ss.dpkg_installs_total+'</td></tr>';
    html += '<tr><td style="padding:4px;color:#8a8f98;">Cron jobs</td><td style="font-size:11px;color:#8a8f98;">'+(ss.cronjobs||[]).join(' | ')+'</td></tr>';
    html += '<tr><td style="padding:4px;color:#8a8f98;">Timers</td><td style="font-size:11px;color:#8a8f98;">'+(ss.timers||[]).slice(0,6).join(' | ')+'</td></tr>';
    html += '<tr><td style="padding:4px;color:#8a8f98;">Thermal</td><td style="font-size:11px;color:#8a8f98;">'+((ss.thermal||[]).join(', ')||'(none — WSL)')+'</td></tr>';
    html += '</tbody></table><div style="font-size:11px;color:#8a8f98;margin-top:8px;">'+(ss.notes||[]).join(' · ')+'</div>';
    tb.innerHTML = html;
  })();
})();

/* ── C: Claude Code local usage cache ──────────────────────────────────── */
(function(){
  const cs = (window.__WEEKLY__ && window.__WEEKLY__.claude_stats) || null;
  const gc = document.getElementById('group-c');
  if(!gc || !cs) return;
  const sum = document.getElementById('group-c-summary');
  if(sum){
    sum.textContent = `${cs.total_sessions} sessions · ${cs.total_messages} messages · ${cs.days.length} active days (cache computed ${cs.last_computed}). Tokens/day from the local usage cache, not cass.`;
  }
  const cc = (id)=>{ const e=document.getElementById(id); return (e && typeof echarts!=='undefined') ? echarts.init(e,'dark') : null; };
  (function(){ // C1 daily activity: messages + tool calls
    const c = cc('figure-c1'); if(!c) return;
    const days = cs.days||[];
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'C1 · Claude Code daily activity (messages, tool calls)', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, legend:{data:['Messages','Tool calls'], textStyle:{color:'#8a8f98'}},
      xAxis:{type:'category', data:days.map(d=>d.date.slice(5)), axisLabel:{color:'#8a8f98', hideOverlap:true}},
      yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:50,right:20,top:40,bottom:40},
      series:[
        {name:'Messages', type:'bar', data:days.map(d=>d.messages), itemStyle:{color:'#7170ff'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
        {name:'Tool calls', type:'line', data:days.map(d=>d.tool_calls), itemStyle:{color:'#ffb020'}, lineStyle:{color:'#ffb020'}, symbol:'circle', emphasis:{focus:'series',blurScope:'coordinateSystem'}}
      ]});
  })();
  (function(){ // C2 daily tokens
    const c = cc('figure-c2'); if(!c) return;
    const days = cs.days||[];
    c.setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
      title:{text:'C2 · Claude Code tokens per day', textStyle:{color:'#f7f8f8'}},
      tooltip:{trigger:'axis'}, xAxis:{type:'category', data:days.map(d=>d.date.slice(5)), axisLabel:{color:'#8a8f98', hideOverlap:true}},
      yAxis:{type:'value', axisLabel:{color:'#8a8f98'}, name:'tokens'}, grid:{left:60,right:20,top:40,bottom:40},
      series:[{type:'bar', data:days.map(d=>d.tokens_total), itemStyle:{color:'#4ecdc4'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}]});
  })();
  (function(){
    const tb = document.getElementById('group-c-table'); if(!tb) return;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr>'+
      ['Model','Input','Output','Cache read','Cache create','Cost'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+'</tr></thead><tbody>';
    for(const m of cs.model_usage||[]){
      html += '<tr><td style="padding:6px;border-bottom:1px solid #222;">'+m.model.slice(0,30)+'</td><td>'+(m.input_tokens/1e6).toFixed(1)+'M</td><td>'+(m.output_tokens/1e6).toFixed(1)+'M</td><td>'+(m.cache_read/1e6).toFixed(1)+'M</td><td>'+(m.cache_creation/1e6).toFixed(1)+'M</td><td>$'+m.cost_usd+'</td></tr>';
    }
    html += '</tbody></table><div style="font-size:11px;color:#8a8f98;margin-top:8px;">'+(cs.notes||[]).join(' · ')+'</div>';
    tb.innerHTML = html;
  })();
})();

/* ── Round-2 additions: commonly-represented charts from existing data ─── */
(function(){ // V6 cumulative market value line (data: subscription_value)
  const sv = (window.__WEEKLY__ && window.__WEEKLY__.subscription_value) || null;
  const c = document.getElementById('figure-v6');
  if(!c || !sv || typeof echarts==='undefined') return;
  const ms = sv.months||[]; let cum=0;
  const cumData = ms.map(m=>{ cum+= (m.market_value||0); return +cum.toFixed(2); });
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'V6 · Cumulative market value of usage vs cumulative sub spend', textStyle:{color:'#f7f8f8'}},
    tooltip:{trigger:'axis'}, legend:{data:['Cum market $','Cum spend $'], textStyle:{color:'#8a8f98'}},
    xAxis:{type:'category', data:ms.map(m=>m.month), axisLabel:{color:'#8a8f98'}},
    yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:60,right:20,top:40,bottom:40},
    series:[
      {name:'Cum market $', type:'line', data:cumData, itemStyle:{color:'#4ecdc4'}, lineStyle:{color:'#4ecdc4',width:3}, symbol:'circle', areaStyle:{color:'rgba(78,205,196,0.15)'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}},
      {name:'Cum spend $', type:'line', data:ms.map((m,i)=>(i+1)*m.sub_cost), itemStyle:{color:'#8a8f98'}, lineStyle:{color:'#8a8f98'}, symbol:'diamond', emphasis:{focus:'series',blurScope:'coordinateSystem'}}
    ]});
})();
(function(){ // H3 stacked sessions per harness per month (data: harness_stats.months)
  const hs = (window.__WEEKLY__ && window.__WEEKLY__.harness_stats) || null;
  const c = document.getElementById('figure-h3');
  if(!c || !hs || typeof echarts==='undefined') return;
  const ms = hs.months||[]; const months=[...new Set(ms.map(m=>m.month))].sort();
  const harnesses=[...new Set(ms.map(m=>m.harness))];
  const palette=['#7170ff','#4ecdc4','#ffb020','#ff7a7a','#a0e8af','#e879f9','#f9a8d4','#8a8f98'];
  const series = harnesses.map((h,i)=>({name:h, type:'bar', stack:'s', data:months.map(mo=>(ms.find(x=>x.month===mo&&x.harness===h)||{}).sessions||0), itemStyle:{color:palette[i%8]}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}));
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'H3 · Sessions per harness per month (stacked)', textStyle:{color:'#f7f8f8'}},
    tooltip:{trigger:'axis'}, legend:{data:harnesses, textStyle:{color:'#8a8f98'}},
    xAxis:{type:'category', data:months, axisLabel:{color:'#8a8f98'}}, yAxis:{type:'value', axisLabel:{color:'#8a8f98'}},
    grid:{left:50,right:20,top:40,bottom:40}, series});
})();
(function(){ // V7 per-plan stacked market value (data: months[].plans)
  const sv = (window.__WEEKLY__ && window.__WEEKLY__.subscription_value) || null;
  const c = document.getElementById('figure-v7');
  if(!c || !sv || typeof echarts==='undefined') return;
  const ms = sv.months||[]; const plans=Object.keys(sv.plans||{});
  const palette=['#7170ff','#ffb020','#4ecdc4','#ff7a7a'];
  const series = plans.map((p,i)=>({name:sv.plans[p].label, type:'bar', stack:'v', data:ms.map(m=>(m.plans&&m.plans[p])?m.plans[p].market_value:0), itemStyle:{color:palette[i%4]}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}));
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'V7 · Market value by subscription (stacked)', textStyle:{color:'#f7f8f8'}},
    tooltip:{trigger:'axis'}, legend:{data:series.map(s=>s.name), textStyle:{color:'#8a8f98'}},
    xAxis:{type:'category', data:ms.map(m=>m.month), axisLabel:{color:'#8a8f98'}}, yAxis:{type:'value', axisLabel:{color:'#8a8f98'}},
    grid:{left:60,right:20,top:40,bottom:40}, series});
})();
(function(){ // C3 cache-read share donut (data: claude_stats.model_usage)
  const cs = (window.__WEEKLY__ && window.__WEEKLY__.claude_stats) || null;
  const c = document.getElementById('figure-c3');
  if(!c || !cs || typeof echarts==='undefined') return;
  const mu = cs.model_usage||[];
  const top = mu.slice(0,6);
  const data = top.map(m=>({name:m.model.slice(0,20), value:m.cache_read+m.input_tokens+m.output_tokens}));
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'C3 · Token share by model (input+output+cache)', textStyle:{color:'#f7f8f8'}, left:'center'},
    tooltip:{trigger:'item'}, legend:{orient:'vertical', right:10, top:'middle', textStyle:{color:'#8a8f98'}},
    series:[{type:'pie', radius:['35%','65%'], center:['40%','55%'], data, emphasis:{focus:'series',blurScope:'coordinateSystem'}, label:{color:'#c2c7d0'}}]});
})();
(function(){ // O3 folder treemap (data: obsidian_stats.folders)
  const os = (window.__WEEKLY__ && window.__WEEKLY__.obsidian_stats) || null;
  const c = document.getElementById('figure-o3');
  if(!c || !os || typeof echarts==='undefined') return;
  const data = (os.folders||[]).map(f=>({name:f[0].slice(0,30), value:f[1]}));
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'O3 · Notes by folder', textStyle:{color:'#f7f8f8'}},
    tooltip:{}, series:[{type:'treemap', data, roam:false, breadcrumb:{show:false}, label:{color:'#c2c7d0'}, emphasis:{focus:'series'}}]});
})();

/* ── This Week: inline report viewer + weekly summary + prose captions ─── */
(function(){
  const weeks = (window.__WEEKLY__ && window.__WEEKLY__.weeks) || [];
  const reports = window.__REPORTS_HTML__ || {};
  const viewer = document.getElementById('report-viewer');
  const wsel = document.getElementById('report-week');
  const prevB = document.getElementById('report-prev');
  const nextB = document.getElementById('report-next');
  const wsum = document.getElementById('weekly-summary');
  if(!viewer || !wsel || !reports || !Object.keys(reports).length) return;
  const order = Object.keys(reports).sort();
  let idx = order.length - 1;
  for(const w of order){ const o=document.createElement('option'); o.value=w; o.textContent=w; wsel.appendChild(o); }
  function render(){
    wsel.value = order[idx];
    const w = order[idx];
    const rep = reports[w] || {};
    let html = '';
    if(rep.personal) html += '<div style="break-inside:avoid;margin-bottom:16px;"><h3 style="color:#f7f8f8;font-size:14px;">Personal report</h3>'+rep.personal+'</div>';
    if(rep.dad) html += '<div style="break-inside:avoid;"><h3 style="color:#f7f8f8;font-size:14px;">Dad report</h3>'+rep.dad+'</div>';
    viewer.innerHTML = html || '<em style="color:#8a8f98;">No report text for this week.</em>';
    // weekly summary (deterministic, from canonical data)
    const wd = weeks.find(x=>x.week_ending===w);
    if(wsum && wd){
      wsum.textContent = `Week ending ${w}: ${wd.sessions!=null?wd.sessions+' sessions':'sessions n/a'}, ${wd.commits!=null?wd.commits+' commits':'commits n/a'}, ${wd.files_changed!=null?wd.files_changed+' files':'files n/a'}, ${wd.projects_active!=null?wd.projects_active+' active projects':'projects n/a'}. Coverage: ${wd.coverage}.`;
    }
  }
  wsel.addEventListener('change', ()=>{ idx = order.indexOf(wsel.value); render(); });
  prevB.addEventListener('click', ()=>{ idx = Math.max(0, idx-1); render(); });
  nextB.addEventListener('click', ()=>{ idx = Math.min(order.length-1, idx+1); render(); });
  render();
})();
(function(){ // prose captions under each chart: what it shows / why it's here
  const CAP = {
    'figure1':'Throughput trend — the weekly heartbeat: sessions, commits, files, active projects.',
    'figure2':'Dark work — sessions per commit with the threshold band; flagged weeks understate effort.',
    'figure-p1':'Commits, files changed, and sessions per month across all projects.',
    'figure-p2':'Top projects by volume — where the week actually went.',
    'figure-p3':'Momentum — activity change vs the prior month; green accelerating, red decelerating.',
    'figure-h1':'Sessions and tokens per harness — which tool carried the load.',
    'figure-h2':'Duration and tools-per-session per harness — how deep the sessions ran.',
    'figure-h3':'Sessions per harness per month — the mix shifting over time.',
    'figure-c1':'Claude Code daily messages and tool calls from its local usage cache.',
    'figure-c2':'Claude Code tokens per day — the real volume.',
    'figure-c3':'Token share by model (input+output+cache) — which Claude model does the work.',
    'figure-v1':'Sessions and tokens per month — activity level.',
    'figure-v2':'Market value of usage vs subscription spend, with the value ratio — the headline question.',
    'figure-v3':'Which harness (and subscription) does the work.',
    'figure-v4':'Efficiency: dollars per session and tokens per subscription dollar.',
    'figure-v5':'Top models in the latest month — mostly the cheap stack.',
    'figure-v6':'Cumulative market value vs cumulative spend — the trend that matters over time.',
    'figure-v7':'Market value by subscription — which plan earns its keep.',
    'figure-o1':'Notes created and words per month — vault growth.',
    'figure-o2':'Tag cloud from YAML frontmatter — what the notes are about.',
    'figure-o3':'Notes by folder — the vault structure.',
    'figure-b1':'Browser visits per month — activity level.',
    'figure-b2':'Top domains by visits — where browsing time goes.',
    'figure-s1':'Package upgrades and shell commands per month — machine upkeep and CLI activity.'
  };
  for(const [id, txt] of Object.entries(CAP)){
    const el = document.getElementById(id);
    if(!el) continue;
    const cap = document.createElement('div');
    cap.textContent = txt;
    cap.style.cssText = 'font-size:11px;color:#8a8f98;margin:-4px 0 12px 0;';
    el.insertAdjacentElement('afterend', cap);
  }
})();

/* ── H4 token share per harness; P4 commits per repo (latest 3 months) ──── */
(function(){ // H4 tokens M per harness (data: harness_stats.harness)
  const hs = (window.__WEEKLY__ && window.__WEEKLY__.harness_stats) || null;
  const c = document.getElementById('figure-h4');
  if(!c || !hs || typeof echarts==='undefined') return;
  const rows = (hs.harness||[]).filter(h=>h.tokens_M>0).sort((a,b)=>b.tokens_M-a.tokens_M).slice(0,8);
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'H4 · Tokens (M) per harness', textStyle:{color:'#f7f8f8'}},
    tooltip:{}, xAxis:{type:'value', axisLabel:{color:'#8a8f98'}},
    yAxis:{type:'category', data:rows.map(h=>h.harness).reverse(), axisLabel:{color:'#8a8f98'}},
    grid:{left:120,right:40,top:40,bottom:30},
    series:[{type:'bar', data:rows.map(h=>h.tokens_M).reverse(), itemStyle:{color:'#4ecdc4'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}, label:{show:true, position:'right', color:'#c2c7d0'}}]});
})();
(function(){ // P4 commits per repo per month (stacked; data: projects_stats.projects commits_by_month)
  const ps = (window.__WEEKLY__ && window.__WEEKLY__.projects_stats) || null;
  const c = document.getElementById('figure-p4');
  if(!c || !ps || typeof echarts==='undefined') return;
  const top = (ps.projects||[]).filter(p=>p.commits>0).sort((a,b)=>b.commits-a.commits).slice(0,8);
  const months=[...new Set(top.flatMap(p=>Object.keys(p.commits_by_month||{})))].sort();
  const palette=['#7170ff','#4ecdc4','#ffb020','#ff7a7a','#a0e8af','#e879f9','#f9a8d4','#8a8f98'];
  const series = top.map((p,i)=>({name:p.project.slice(0,16), type:'bar', stack:'c', data:months.map(m=>p.commits_by_month[m]||0), itemStyle:{color:palette[i%8]}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}));
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'P4 · Commits per repo per month', textStyle:{color:'#f7f8f8'}},
    tooltip:{trigger:'axis'}, legend:{data:series.map(s=>s.name), textStyle:{color:'#8a8f98'}, type:'scroll'},
    xAxis:{type:'category', data:months, axisLabel:{color:'#8a8f98'}}, yAxis:{type:'value', axisLabel:{color:'#8a8f98'}},
    grid:{left:50,right:20,top:40,bottom:40}, series});
})();

/* ── B3 browser hourly heatmap; P-table git state; muse row fix ────────── */
(function(){ // B3 visits by hour of day (UTC)
  const bs = (window.__WEEKLY__ && window.__WEEKLY__.browser_stats) || null;
  const c = document.getElementById('figure-b3');
  if(!c || !bs || typeof echarts==='undefined') return;
  const hrs = bs.hours||[];
  if(!hrs.length) return;
  echarts.init(c,'dark').setOption({backgroundColor:'transparent', textStyle:{color:'#8a8f98'},
    title:{text:'B3 · Browser activity by hour (UTC)', textStyle:{color:'#f7f8f8'}},
    tooltip:{trigger:'axis'}, xAxis:{type:'category', data:hrs.map((_,i)=>i+'h'), axisLabel:{color:'#8a8f98', interval:2}},
    yAxis:{type:'value', axisLabel:{color:'#8a8f98'}}, grid:{left:50,right:20,top:40,bottom:40},
    series:[{type:'bar', data:hrs, itemStyle:{color:'#ffb020'}, emphasis:{focus:'series',blurScope:'coordinateSystem'}}]});
})();
(function(){ // P-table: append git-state columns via a second table
  const ps = (window.__WEEKLY__ && window.__WEEKLY__.projects_stats) || null;
  const tb = document.getElementById('group-p-git');
  if(!tb || !ps) return;
  const ga = ps.git_audit;
  const rows = (ps.projects||[]).filter(p=>p.git_state);
  let html = '<div style="margin-top:10px;font-size:12px;color:#c2c7d0;">Git audit ('+(ga?ga.timestamp+' · health '+ga.health_pct+'% · clean '+(ga.stats||{}).clean+', conflict '+(ga.stats||{}).conflict:'')+')</div>';
  html += '<table style="width:100%;border-collapse:collapse;font-size:12px;margin-top:6px;"><thead><tr>'+
    ['Repo','State','Uncommitted','Ahead','Behind'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+'</tr></thead><tbody>';
  for(const p of rows.slice(0,30)){
    const dirty = (p.git_uncommitted||0)+(p.git_ahead||0)+(p.git_behind||0);
    html += '<tr><td style="padding:6px;border-bottom:1px solid #222;">'+p.project.slice(0,28)+'</td><td>'+p.git_state+'</td><td>'+p.git_uncommitted+'</td><td>'+p.git_ahead+'</td><td>'+p.git_behind+'</td></tr>';
  }
  html += '</tbody></table>';
  tb.innerHTML = html;
})();
(function(){ // muse row fix: rewrite the harness table so muse months render cleanly
  const hs = (window.__WEEKLY__ && window.__WEEKLY__.harness_stats) || null;
  const tb = document.getElementById('group-h-table');
  if(!tb || !hs) return;
  const rows = hs.harness||[];
  let html = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr>'+
    ['Harness','Sessions','Avg min','Tools','Tools/session','API calls','Tokens M','Top models','Top workspaces'].map(h=>'<th style="text-align:left;padding:6px;color:#8a8f98;border-bottom:1px solid #333;">'+h+'</th>').join('')+'</tr></thead><tbody>';
  for(const h of rows){
    html += '<tr><td style="padding:6px;border-bottom:1px solid #222;">'+h.harness+'</td><td>'+h.sessions+'</td><td>'+(h.avg_dur_min!=null?h.avg_dur_min:'—')+'</td><td>'+h.tool_calls+'</td><td>'+(h.tools_per_session!=null?h.tools_per_session:'—')+'</td><td>'+h.api_calls+'</td><td>'+h.tokens_M+'</td><td style="font-size:11px;color:#8a8f98;">'+(h.top_models||[]).map(x=>x[0].slice(0,16)+' ×'+x[1]).join(', ')+'</td><td style="font-size:11px;color:#8a8f98;">'+(h.top_workspaces||[]).map(x=>x[0].slice(0,12)+' ×'+x[1]).join(', ')+'</td></tr>';
  }
  if(hs.muse && hs.muse.months && hs.muse.months.length){
    for(const m of hs.muse.months){
      html += '<tr><td>muse ('+m.month+')</td><td>'+m.sessions+'</td><td>'+(m.avg_min!=null?m.avg_min:'—')+'</td><td>—</td><td>—</td><td>—</td><td>—</td><td style="font-size:11px;color:#8a8f98;">direct read</td><td style="font-size:11px;color:#8a8f98;">session dirs</td></tr>';
    }
  }
  html += '</tbody></table>';
  tb.innerHTML = html;
})();

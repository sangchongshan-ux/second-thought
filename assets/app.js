/**
 * Second Thought — session logic.
 *
 * Design notes that matter for the report:
 *  - Help is a ladder the learner climbs deliberately (levels 1-3), never an answer.
 *  - The hint level offered is chosen by a small, explainable rule set, and the
 *    interface states which rule fired ("Because this is your second attempt").
 *  - The reflection prompt is tied to the end of a problem, not to a clock, so it
 *    cannot interrupt someone mid-reasoning.
 *  - The summary always carries a limits statement: the numbers describe help use
 *    in one sitting, not ability.
 */
(function () {
  'use strict';

  const { PROBLEMS, parseAnswer, isCorrect, isLure } = window.ProblemBank;
  const STORE_KEY = 'second-thought:session:v1';

  const $ = id => document.getElementById(id);
  const now = () => Date.now();

  let state = null;
  let tick = null;

  /* ── persistence ─────────────────────────────────────────────── */

  function blankSession(logging) {
    return {
      schema: 1,
      startedAt: new Date().toISOString(),
      logging: logging,
      index: 0,
      records: [],
      reflections: [],
      events: []
    };
  }

  function currentRecord() {
    return state.records[state.index] || null;
  }

  function ensureRecord() {
    let r = currentRecord();
    if (!r) {
      r = {
        id: PROBLEMS[state.index].id,
        attempts: [],
        hints: [],
        reflections: [],
        startedAt: now(),
        ms: 0,
        solved: false,
        outcome: 'in-progress'
      };
      state.records[state.index] = r;
    }
    return r;
  }

  function log(type, extra) {
    if (!state.logging) return;
    state.events.push(Object.assign({ t: now(), type: type }, extra || {}));
  }

  function persist() {
    if (!state || !state.logging) return;
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) { /* storage full or blocked */ }
  }

  function load() {
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (!raw) return null;
      const s = JSON.parse(raw);
      return s && s.schema === 1 ? s : null;
    } catch (e) { return null; }
  }

  function wipe() {
    try { localStorage.removeItem(STORE_KEY); } catch (e) { /* ignore */ }
  }

  /* ── view plumbing ───────────────────────────────────────────── */

  function show(view) {
    ['contract', 'task', 'summary'].forEach(v => { $('view-' + v).hidden = (v !== view); });
    window.scrollTo({ top: 0, behavior: 'instant' in document.documentElement.style ? 'instant' : 'auto' });
  }

  function setPill(text, kind) {
    const el = $('record-pill');
    el.textContent = text;
    el.className = 'pill ' + (kind || 'pill-quiet');
  }

  /* ── task rendering ──────────────────────────────────────────── */

  function renderTask() {
    const p = PROBLEMS[state.index];
    const r = ensureRecord();

    $('progress').textContent = 'Problem ' + (state.index + 1) + ' of ' + PROBLEMS.length;
    $('problem-heading').textContent = p.prompt;
    $('unit').textContent = p.unit;
    $('answer').value = '';
    $('answer').disabled = false;
    $('feedback').hidden = true;
    $('feedback').replaceChildren();
    $('hint-box').hidden = true;
    $('reflect').hidden = true;
    $('reflect-input').value = '';
    $('stuck-btn').hidden = false;

    renderDots();
    startTimer();
    $('answer').focus();
  }

  function renderDots() {
    const ol = $('dots');
    ol.replaceChildren();
    PROBLEMS.forEach((p, i) => {
      const li = document.createElement('li');
      const rec = state.records[i];
      let cls = 'dot';
      if (rec && rec.solved) cls += ' dot-done';
      else if (rec && rec.outcome === 'left') cls += ' dot-left';
      else if (i === state.index) cls += ' dot-now';
      li.className = cls;
      li.title = 'Problem ' + (i + 1);
      ol.append(li);
    });
  }

  function startTimer() {
    clearInterval(tick);
    const t0 = now();
    const base = currentRecord() ? currentRecord().ms : 0;
    const paint = () => {
      const s = Math.floor((base + now() - t0) / 1000);
      $('timer').textContent = Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    };
    paint();
    tick = setInterval(paint, 1000);
  }

  function stopTimer() {
    clearInterval(tick);
    tick = null;
  }

  /* ── the hint ladder ─────────────────────────────────────────── */

  /** Rule set: which level to offer next, and the sentence that explains why. */
  function chooseLevel(record) {
    const wrong = record.attempts.filter(a => !a.correct).length;
    const deepest = record.hints.length ? Math.max.apply(null, record.hints.map(h => h.level)) : 0;
    const hitLure = record.attempts.some(a => a.lure);

    if (hitLure && wrong >= 1) {
      return { level: Math.max(2, deepest), why: 'because your answer matched the trap this problem is built around' };
    }
    if (wrong >= 2) {
      return { level: 3, why: 'because this is at least your third attempt' };
    }
    if (wrong === 1) {
      return { level: 2, why: 'because you have already tried once' };
    }
    if (deepest > 0) {
      return { level: Math.min(3, deepest + 1), why: 'because you asked to go one step further' };
    }
    return { level: 1, why: 'because you have not answered yet' };
  }

  function showHint(deeper) {
    const p = PROBLEMS[state.index];
    const r = ensureRecord();
    const deepest = r.hints.length ? Math.max.apply(null, r.hints.map(h => h.level)) : 0;
    const choice = deeper
      ? { level: Math.min(3, deepest + 1), why: 'because you asked to go one step further' }
      : chooseLevel(r);
    const level = choice.level;

    if (level > r.hints.length) {
      r.hints.push({ level: level, at: now() });
      log('hint', { problem: p.id, level: level });
    }

    $('hint-level').textContent = 'Hint ' + level + ' of 3';
    $('hint-why').textContent = choice.why;
    $('hint-text').textContent = p.hints[level - 1];
    $('hint-box').hidden = false;
    $('deeper-btn').hidden = level >= 3;
    $('stuck-btn').hidden = false;
    $('stuck-btn').textContent = 'Show the hint again';
    persist();
  }

  /* ── answering ───────────────────────────────────────────────── */

  function feedback(html, actions) {
    const box = $('feedback');
    box.hidden = false;
    box.replaceChildren();
    const body = document.createElement('div');
    body.className = 'feedback-body';
    body.innerHTML = html;
    box.append(body);
    if (actions && actions.length) {
      const row = document.createElement('div');
      row.className = 'feedback-actions';
      actions.forEach(a => {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = a.kind === 'primary' ? 'primary small-btn' : 'ghost small-btn';
        b.textContent = a.label;
        b.onclick = a.onClick;
        row.append(b);
      });
      box.append(row);
    }
  }

  function submitAnswer(ev) {
    ev.preventDefault();
    const p = PROBLEMS[state.index];
    const r = ensureRecord();
    const raw = $('answer').value;
    const value = parseAnswer(raw);
    if (value === null) {
      feedback('<p>Type a number — digits only is fine, units are optional.</p>');
      return;
    }

    const correct = isCorrect(p, value);
    const lure = isLure(p, value);
    const elapsed = now() - r.startedAt;

    r.attempts.push({ value: value, correct: correct, lure: lure, at: now() });
    log('attempt', { problem: p.id, correct: correct, lure: lure });
    persist();

    const wrongCount = r.attempts.filter(a => !a.correct).length;

    if (correct) {
      r.solved = true;
      r.outcome = r.hints.length ? 'solved-with-support' : 'solved-unaided';
      r.ms = elapsed;
      stopTimer();
      $('answer').disabled = true;
      const support = r.hints.length
        ? ' You got there with hint ' + Math.max.apply(null, r.hints.map(h => h.level)) + '.'
        : ' You solved it without asking for help.';
      feedback('<p><strong>Correct.</strong>' + support + '</p>', []);
      log('solved', { problem: p.id, hints: r.hints.length });
      openReflection();
      renderDots();
      return;
    }

    // wrong
    const seconds = Math.round(elapsed / 1000);
    let msg = '<p><strong>Not yet.</strong> ';
    if (lure) {
      msg += p.lureNote + '</p><p class="small">You can try again, or ask for the next step.';
    } else if (seconds < 15) {
      msg += 'You answered in ' + seconds + ' seconds. Write the relationship down before you try again.';
    } else {
      msg += 'Check the relationship you set up, and the units, before you try again.';
    }
    msg += '</p>';

    const actions = [];
    if (wrongCount >= 3) {
      actions.push({
        label: 'Leave this problem and move on',
        kind: 'ghost',
        onClick: () => {
          r.outcome = 'left';
          r.ms = now() - r.startedAt;
          stopTimer();
          log('left', { problem: p.id });
          persist();
          openReflection();
        }
      });
    }
    feedback(msg, actions);
    renderDots();
  }

  /* ── reflection, tied to the end of a problem ────────────────── */

  function openReflection() {
    $('stuck-btn').hidden = true;
    $('hint-box').hidden = true;
    $('reflect').hidden = false;
    $('reflect-input').focus();
  }

  function closeReflection(text) {
    const r = currentRecord();
    if (text && text.trim()) {
      r.reflections.push(text.trim());
      state.reflections.push({ problem: r.id, text: text.trim(), at: now() });
      log('reflection', { problem: r.id });
    }
    persist();
    nextProblem();
  }

  function nextProblem() {
    stopTimer();
    if (state.index >= PROBLEMS.length - 1) {
      finish();
      return;
    }
    state.index += 1;
    persist();
    renderTask();
  }

  /* ── summary ─────────────────────────────────────────────────── */

  function summarise() {
    const recs = state.records.filter(Boolean);
    const unaided = recs.filter(r => r.outcome === 'solved-unaided').length;
    const supported = recs.filter(r => r.outcome === 'solved-with-support').length;
    const left = recs.filter(r => r.outcome === 'left').length;
    const deepest = recs.reduce((m, r) => Math.max(m, r.hints.length ? Math.max.apply(null, r.hints.map(h => h.level)) : 0), 0);
    const hintsUsed = recs.reduce((n, r) => n + r.hints.length, 0);
    const lures = recs.reduce((n, r) => n + r.attempts.filter(a => a.lure).length, 0);
    const times = recs.map(r => Math.round(r.ms / 1000));
    const total = times.reduce((a, b) => a + b, 0);
    return { recs, unaided, supported, left, deepest, hintsUsed, lures, times, total };
  }

  function profileFor(s) {
    if (s.unaided === PROBLEMS.length) {
      return {
        label: 'Independent on this set',
        line: 'You solved all three without asking for help, and you did not take the intuitive answer on any of them.'
      };
    }
    if (s.deepest >= 3) {
      return {
        label: 'Carried by the last step',
        line: 'You reached the worked step on at least one problem. That is a reasonable thing to do — but it is the level where the reasoning is being done for you rather than with you.'
      };
    }
    if (s.supported > 0) {
      return {
        label: 'Support used, then finished',
        line: 'You asked for help and then completed the reasoning yourself. This is the pattern the design is trying to make easy.'
      };
    }
    return {
      label: 'Stopped short',
      line: 'At least one problem was left unsolved. That is recorded as it happened, not as a failure.'
    };
  }

  function renderSummary() {
    const s = summarise();
    const p = profileFor(s);

    const metrics = $('metrics');
    metrics.replaceChildren();
    [
      ['Solved without help', s.unaided + ' / ' + PROBLEMS.length],
      ['Solved with hints', s.supported + ' / ' + PROBLEMS.length],
      ['Deepest hint level', s.deepest + ' of 3'],
      ['Hints requested', String(s.hintsUsed)],
      ['Time on the set', Math.floor(s.total / 60) + 'm ' + (s.total % 60) + 's']
    ].forEach(([k, v]) => {
      const d = document.createElement('div');
      d.className = 'metric';
      const kk = document.createElement('span'); kk.className = 'metric-k'; kk.textContent = k;
      const vv = document.createElement('span'); vv.className = 'metric-v'; vv.textContent = v;
      d.append(kk, vv);
      metrics.append(d);
    });

    $('profile-label').textContent = p.label;
    $('profile-line').textContent = p.line;

    const lureNote = s.lures
      ? ' You gave the intuitive answer ' + s.lures + (s.lures === 1 ? ' time' : ' times') + ' before correcting or leaving it.'
      : '';
    $('profile-limits').textContent =
      'This describes how you used help on these three problems in this sitting.' + lureNote +
      ' It is not a measure of your ability, and it does not show whether you understood the reasoning: ' +
      'finishing after a level-3 hint and finishing alone can both teach you something. ' +
      'It also cannot tell you how you would do on a similar problem tomorrow — that would need a delayed ' +
      'retest without support, which this prototype does not run.';

    const body = $('detail-body');
    body.replaceChildren();
    PROBLEMS.forEach((prob, i) => {
      const r = state.records[i];
      const tr = document.createElement('tr');
      const cells = [
        String(i + 1),
        r ? String(r.attempts.length) : '—',
        r && r.hints.length ? String(Math.max.apply(null, r.hints.map(h => h.level))) : 'none',
        r ? Math.round(r.ms / 1000) + 's' : '—',
        r ? r.outcome.replace(/-/g, ' ') : 'not started'
      ];
      cells.forEach(c => { const td = document.createElement('td'); td.textContent = c; tr.append(td); });
      body.append(tr);
    });

    show('summary');
  }

  function finish() {
    stopTimer();
    log('session-end');
    persist();
    setPill(state.logging ? 'Session recorded' : 'Not recorded', 'pill-quiet');
    renderSummary();
  }

  /* ── export / delete / restart ───────────────────────────────── */

  function exportSession() {
    const payload = {
      app: 'Second Thought',
      exportedAt: new Date().toISOString(),
      schema: state.schema,
      session: state,
      summary: (() => { const s = summarise(); return {
        unaided: s.unaided, supported: s.supported, left: s.left,
        deepestHintLevel: s.deepest, hintsRequested: s.hintsUsed, lureAnswers: s.lures,
        seconds: s.times
      }; })()
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'second-thought-session.json';
    document.body.append(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
    $('data-status').textContent = 'Exported second-thought-session.json';
    log('export');
    persist();
  }

  function deleteSession() {
    if (!confirm('Delete this session from this browser? This cannot be undone.')) return;
    wipe();
    state = null;
    setPill('Not started', 'pill-quiet');
    $('data-status').textContent = '';
    show('contract');
  }

  function restart() {
    wipe();
    state = null;
    setPill('Not started', 'pill-quiet');
    $('data-status').textContent = '';
    show('contract');
    $('start-btn').focus();
  }

  /* ── boot ────────────────────────────────────────────────────── */

  function startSession() {
    state = blankSession($('logging-toggle').checked);
    log('session-start');
    persist();
    setPill(state.logging ? 'Recording' : 'Not recording', state.logging ? 'pill-live' : 'pill-quiet');
    show('task');
    renderTask();
  }

  function boot() {
    const stored = load();
    if (stored && stored.records && stored.records.length) {
      state = stored;
      setPill(state.logging ? 'Session restored' : 'Not recorded', 'pill-quiet');
      if (state.records.length >= PROBLEMS.length && state.records.every(r => r && r.outcome && r.outcome !== 'in-progress')) {
        renderSummary();
      } else {
        state.index = Math.min(state.index, PROBLEMS.length - 1);
        show('task');
        renderTask();
      }
      return;
    }
    show('contract');
  }

  $('start-btn').addEventListener('click', startSession);
  $('answer-form').addEventListener('submit', submitAnswer);
  $('stuck-btn').addEventListener('click', () => showHint(false));
  $('deeper-btn').addEventListener('click', () => showHint(true));
  $('hide-hint-btn').addEventListener('click', () => { $('hint-box').hidden = true; });
  $('reflect-save').addEventListener('click', () => closeReflection($('reflect-input').value));
  $('reflect-skip').addEventListener('click', () => closeReflection(''));
  $('export-btn').addEventListener('click', exportSession);
  $('delete-btn').addEventListener('click', deleteSession);
  $('restart-btn').addEventListener('click', restart);
  $('about-btn').addEventListener('click', () => $('about').showModal());
  $('logging-toggle').addEventListener('change', e => {
    $('logging-note').textContent = e.target.checked
      ? 'Recorded in this browser only. You can export or delete it from the summary screen.'
      : 'Not recorded. The summary will still be computed while this tab is open, then lost when you close it.';
  });

  boot();
})();

const scenarios = {
  pass: {
    outcome: 'Inserted',
    tone: '',
    steps: ['done', 'done', 'done'],
    log: '[validate] 2 events pass the source contract\n[merge] 2 unseen event IDs inserted\n[read] Delta table contains 2 unique events',
    explanation: 'A valid first batch reaches MERGE. The Delta table records each unseen event ID once.'
  },
  fail: {
    outcome: 'Held back',
    tone: 'failed',
    steps: ['stop', '', 'done'],
    log: '[validate] power_kw is not finite\n[merge] skipped: no table write attempted\n[read] Delta version unchanged; previous row remains',
    explanation: 'Validation rejects the full batch before MERGE. The test checks that the Delta transaction version does not move.'
  },
  replay: {
    outcome: 'No duplicates',
    tone: 'unknown',
    steps: ['done', 'done', 'done'],
    log: '[validate] 2 repeated events pass the source contract\n[merge] 0 unseen event IDs inserted\n[read] same 2 unique events remain visible',
    explanation: 'MERGE matches on event ID. Replaying a valid batch changes no visible rows in the tested reference.'
  }
};

function showScenario(name) {
  const selected = scenarios[name];
  if (!selected) return;
  document.querySelectorAll('.scenario').forEach(button => {
    const active = button.dataset.scenario === name;
    button.classList.toggle('is-active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  const badge = document.getElementById('outcome-tag');
  badge.textContent = selected.outcome;
  badge.className = `output-indicator ${selected.tone}`.trim();
  document.querySelectorAll('.trace-step').forEach((step, index) => {
    step.classList.remove('done', 'wait', 'stop');
    if (selected.steps[index]) step.classList.add(selected.steps[index]);
  });
  document.getElementById('trace-log').textContent = selected.log;
  document.getElementById('trace-explainer').textContent = selected.explanation;
}

document.querySelectorAll('.scenario').forEach(button => {
  button.addEventListener('click', () => showScenario(button.dataset.scenario));
});
showScenario('pass');

async function initCodeTabs() {
  const display = document.querySelector('#code-display code');
  let samples;
  try {
    const response = await fetch('assets/code-snippets.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    samples = await response.json();
  } catch (error) {
    display.textContent = 'Source excerpts could not be loaded. Please try again or request the full Nexus source.';
    return;
  }

  const tabs = [...document.querySelectorAll('.code-tab')];
  function showCode(key, focus = false) {
    const sample = samples[key];
    if (!sample) return;
    tabs.forEach(tab => {
      const active = tab.dataset.code === key;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    display.textContent = sample.code;
    document.getElementById('code-filename').textContent = sample.filename;
    document.getElementById('code-language').textContent = sample.language;
    document.getElementById('code-source').textContent = sample.source;
    const link = document.getElementById('code-link');
    link.href = sample.link;
    link.innerHTML = `${sample.linkText} <span aria-hidden="true">↗</span>`;
    document.getElementById('code-display').setAttribute('aria-labelledby', `tab-${key}`);
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => showCode(tab.dataset.code));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      showCode(tabs[next].dataset.code, true);
    });
  });
  showCode('nexus');
}

initCodeTabs();

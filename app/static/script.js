(function() {
  const clearBtn = document.getElementById('btn-clear');
  const copyBtn = document.getElementById('btn-copy-result');
  const toast = document.getElementById('toast');
  const themeToggle = document.getElementById('theme-toggle');

  // Fields lookup
  const inputs = {
    cement: document.getElementById('cement'),
    blast_furnace_slag: document.getElementById('blast_furnace_slag'),
    fly_ash: document.getElementById('fly_ash'),
    water: document.getElementById('water'),
    superplasticizer: document.getElementById('superplasticizer'),
    coarse_aggregate: document.getElementById('coarse_aggregate'),
    fine_aggregate: document.getElementById('fine_aggregate'),
    age: document.getElementById('age')
  };

  // Theme switching (saved to localStorage)
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (themeToggle) {
      const isDark = theme === 'dark';
      themeToggle.setAttribute('title', isDark ? 'Switch to light mode' : 'Switch to dark mode');
      themeToggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }

  function initTheme() {
    const savedTheme = localStorage.getItem('cs_theme') || 'light';
    applyTheme(savedTheme);
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('cs_theme', next);
    });
  }
  initTheme();

  // Toast feedback
  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('visible');
    setTimeout(() => {
      toast.classList.remove('visible');
    }, 2400);
  }

  // Live mix calculation
  function updateLiveAnalytics() {
    const getVal = (input) => {
      if (!input) return 0;
      const v = parseFloat(input.value);
      return isNaN(v) ? 0 : v;
    };

    const cement = getVal(inputs.cement);
    const slag = getVal(inputs.blast_furnace_slag);
    const flyAsh = getVal(inputs.fly_ash);
    const water = getVal(inputs.water);
    const sp = getVal(inputs.superplasticizer);
    const coarse = getVal(inputs.coarse_aggregate);
    const fine = getVal(inputs.fine_aggregate);

    const binder = cement + slag + flyAsh;
    const aggregate = coarse + fine;
    const density = binder + water + sp + aggregate;
    const wbRatio = binder > 0 ? (water / binder) : 0;

    const calcWb = document.getElementById('calc-wb');
    const calcBinder = document.getElementById('calc-binder');
    const calcAgg = document.getElementById('calc-aggregate');
    const calcDensity = document.getElementById('calc-density');

    if (calcWb) calcWb.textContent = binder > 0 ? wbRatio.toFixed(2) : '—';
    if (calcBinder) calcBinder.textContent = binder > 0 ? Math.round(binder) + ' kg' : '—';
    if (calcAgg) calcAgg.textContent = aggregate > 0 ? Math.round(aggregate) + ' kg' : '—';
    if (calcDensity) calcDensity.textContent = density > 0 ? Math.round(density) + ' kg' : '—';
  }

  // Attach input listeners for live metrics
  Object.values(inputs).forEach(input => {
    if (input) {
      input.addEventListener('input', updateLiveAnalytics);
    }
  });
  updateLiveAnalytics();

  // Clear button
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      // 1. Clear input values & validation attributes
      Object.values(inputs).forEach(input => {
        if (input) {
          input.value = '';
          input.removeAttribute('aria-invalid');
        }
      });

      // 2. Hide error messages
      document.querySelectorAll('.error').forEach(e => {
        e.style.display = 'none';
      });

      // 3. Reset prediction display to ready state (≈ 0 MPa)
      const predictionVal = document.getElementById('prediction-result-val');
      const predictionExact = document.getElementById('prediction-exact-val');
      const meterFill = document.getElementById('prediction-meter-fill');
      const badgeText = document.getElementById('prediction-badge-text');

      if (predictionVal) predictionVal.textContent = '≈ 0 MPa';
      if (predictionExact) predictionExact.textContent = '0.00 MPa';
      if (meterFill) meterFill.style.width = '0%';
      if (badgeText) badgeText.textContent = 'Ready for Prediction';

      // 4. Clean browser history state
      if (window.history && window.history.replaceState) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      // 5. Reset live ratio calculations
      updateLiveAnalytics();
    });
  }

  // Copy button
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const text = copyBtn.getAttribute('data-result') || '';
      navigator.clipboard.writeText(text).then(() => {
        showToast('Copied: ' + text);
      }).catch(() => {
        showToast('Failed to copy');
      });
    });
  }
})();

(function () {
  const select = document.getElementById('model');
  const dataElement = document.getElementById('evaluation-data');
  if (!select || !dataElement) return;
  const metrics = JSON.parse(dataElement.textContent);
  select.addEventListener('change', function () {
    const score = metrics[select.value];
    if (!score) return;
    document.getElementById('evaluation-model-label').textContent = score.label;
    document.getElementById('metric-mae').textContent = score.MAE.toFixed(2);
    document.getElementById('metric-rmse').textContent = score.RMSE.toFixed(2);
    document.getElementById('metric-r2').textContent = score.R2.toFixed(4);
    document.querySelectorAll('[data-evaluation-model]').forEach(function (row) {
      row.classList.toggle('selected-metric-row', row.dataset.evaluationModel === select.value);
    });
  });
})();

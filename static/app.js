(function () {
  // --- Autocomplete ---

  let selectedNeighborhoodPlaceId = '';

  function setupAutocomplete(inputEl, listEl, kind, getCityValue) {
    let debounceTimer = null;
    let activeIndex = -1;

    function getItems() {
      return listEl.querySelectorAll('li');
    }

    function closeSuggestions() {
      listEl.classList.add('hidden');
      listEl.innerHTML = '';
      activeIndex = -1;
    }

    function selectItem(value, placeId) {
      inputEl.value = value;
      if (kind === 'neighborhood') {
        selectedNeighborhoodPlaceId = placeId || '';
      }
      closeSuggestions();
    }

    function renderSuggestions(suggestions) {
      listEl.innerHTML = '';
      activeIndex = -1;
      if (!suggestions.length) { closeSuggestions(); return; }

      suggestions.forEach((s) => {
        const li = document.createElement('li');
        li.className =
          'px-3 py-2 text-sm text-gray-700 cursor-pointer hover:bg-indigo-50 hover:text-indigo-700 dark:text-[#9897b3] dark:hover:bg-[#252340] dark:hover:text-[#e2e1f0] transition-colors';
        li.textContent = s.label;
        li.dataset.value = s.value;
        li.dataset.placeId = s.place_id || '';
        li.addEventListener('mousedown', (e) => {
          e.preventDefault();
          selectItem(s.value, s.place_id);
        });
        listEl.appendChild(li);
      });

      listEl.classList.remove('hidden');
    }

    function highlightItem(index) {
      const items = getItems();
      const isDark = document.documentElement.classList.contains('dark');
      items.forEach((el, i) => {
        const active = i === index;
        el.classList.toggle('bg-indigo-50', active && !isDark);
        el.classList.toggle('text-indigo-700', active && !isDark);
        el.classList.toggle('highlighted', active);
      });
    }

    inputEl.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      if (kind === 'neighborhood') selectedNeighborhoodPlaceId = '';
      const val = inputEl.value.trim();
      if (val.length < 2) { closeSuggestions(); return; }

      debounceTimer = setTimeout(async () => {
        const city = getCityValue ? getCityValue() : '';
        const params = new URLSearchParams({ input: val, kind });
        if (city) params.set('city', city);

        try {
          const res = await fetch(`/autocomplete?${params}`);
          const data = await res.json();
          renderSuggestions(data.suggestions || []);
        } catch {
          closeSuggestions();
        }
      }, 300);
    });

    inputEl.addEventListener('keydown', (e) => {
      const items = getItems();
      if (!items.length) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, items.length - 1);
        highlightItem(activeIndex);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        highlightItem(activeIndex);
      } else if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        const el = items[activeIndex];
        selectItem(el.dataset.value, el.dataset.placeId);
      } else if (e.key === 'Escape') {
        closeSuggestions();
      }
    });

    inputEl.addEventListener('blur', () => {
      setTimeout(closeSuggestions, 150);
    });
  }

  const cityInput = document.getElementById('city');
  const cityList = document.getElementById('citySuggestions');
  const neighborhoodInput = document.getElementById('neighborhood');
  const neighborhoodList = document.getElementById('neighborhoodSuggestions');

  setupAutocomplete(cityInput, cityList, 'city', null);
  setupAutocomplete(neighborhoodInput, neighborhoodList, 'neighborhood', () => cityInput.value.trim());

  // --- Search form ---

  const form = document.getElementById('searchForm');
  const searchBtn = document.getElementById('searchBtn');
  const searchBtnText = document.getElementById('searchBtnText');
  const spinner = document.getElementById('spinner');

  const emptyState = document.getElementById('emptyState');
  const noResultsState = document.getElementById('noResultsState');
  const summaryBar = document.getElementById('summaryBar');
  const summaryText = document.getElementById('summaryText');
  const resultsCard = document.getElementById('resultsCard');
  const resultsBody = document.getElementById('resultsBody');
  const resultsCount = document.getElementById('resultsCount');
  const exportBtn = document.getElementById('exportBtn');

  function setLoading(loading) {
    searchBtn.disabled = loading;
    spinner.classList.toggle('hidden', !loading);
    searchBtnText.textContent = loading ? 'Buscando...' : 'Buscar Negócios';
    searchBtn.classList.toggle('opacity-75', loading);
  }

  function hideAll() {
    emptyState.classList.add('hidden');
    noResultsState.classList.add('hidden');
    summaryBar.classList.add('hidden');
    resultsCard.classList.add('hidden');
  }

  function buildWebsiteBadge(hasWebsite) {
    if (hasWebsite) {
      return '<span class="badge-has-site inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Sim</span>';
    }
    return '<span class="badge-no-site inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">Não</span>';
  }

  function buildMapsLink(url) {
    if (!url) return '<span class="text-gray-300 dark:text-[#3a3858] text-xs">—</span>';
    return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer"
      class="maps-link inline-flex items-center gap-1 text-brand-600 hover:text-brand-500 font-medium text-xs transition-colors">
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
      </svg>Abrir</a>`;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderResults(data) {
    const { results, summary } = data;

    hideAll();

    const parts = [];
    parts.push(`<span class="text-brand-600 font-bold">${summary.new_saved}</span> novos encontrados`);
    parts.push(`<span class="text-green-600 font-bold">${summary.without_website}</span> sem site`);
    parts.push(`<span class="text-gray-400">${summary.skipped_duplicates}</span> já vistos antes`);

    summaryText.innerHTML = parts.join(' &nbsp;&middot;&nbsp; ');
    summaryBar.classList.remove('hidden');
    summaryBar.classList.add('fade-in');

    if (results.length === 0) {
      noResultsState.classList.remove('hidden');
      noResultsState.classList.add('fade-in');
      return;
    }

    resultsBody.innerHTML = results.map(biz => `
      <tr class="hover:bg-gray-50 transition-colors">
        <td class="cell-name px-4 py-3 font-medium text-gray-800">${escapeHtml(biz.name)}</td>
        <td class="cell-addr px-4 py-3 text-gray-500 max-w-xs">
          <span class="block truncate" title="${escapeHtml(biz.address)}">${escapeHtml(biz.address)}</span>
        </td>
        <td class="cell-phone px-4 py-3 text-gray-600 whitespace-nowrap">${escapeHtml(biz.phone)}</td>
        <td class="px-4 py-3 text-center">${buildWebsiteBadge(biz.has_website)}</td>
        <td class="px-4 py-3 text-center">${buildMapsLink(biz.maps_url)}</td>
      </tr>
    `).join('');

    resultsCount.textContent = `${results.length} resultado${results.length !== 1 ? 's' : ''}`;
    resultsCard.classList.remove('hidden');
    resultsCard.classList.add('fade-in');

    // Update export button to reflect current filter
    const onlyWithout = document.getElementById('only_without_website').checked;
    exportBtn.href = onlyWithout ? '/export?only_without_website=true' : '/export';
  }

  function showError(message) {
    hideAll();
    noResultsState.classList.remove('hidden');
    noResultsState.classList.add('fade-in');
    noResultsState.querySelector('h3').textContent = 'Erro ao buscar';
    noResultsState.querySelector('p').textContent = message;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    setLoading(true);

    const payload = {
      city: document.getElementById('city').value.trim(),
      neighborhood: document.getElementById('neighborhood').value.trim(),
      business_type: document.getElementById('business_type').value,
      quantity: parseInt(document.getElementById('quantity').value, 10),
      only_without_website: document.getElementById('only_without_website').checked,
      neighborhood_place_id: selectedNeighborhoodPlaceId,
    };

    try {
      const response = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        showError(data.detail || 'Erro desconhecido.');
        return;
      }

      renderResults(data);
    } catch (err) {
      showError('Não foi possível conectar ao servidor. Tente novamente.');
    } finally {
      setLoading(false);
    }
  });
})();

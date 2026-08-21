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
          if (res.status === 401) {
            window.location.assign('/login?return_to=' + encodeURIComponent(window.location.pathname));
            return;
          }
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

  // --- Business type combobox ---

  function normalizeText(value) {
    return String(value)
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();
  }

  function loadBusinessTypes() {
    const el = document.getElementById('businessTypesData');
    if (!el) return [];
    try {
      return JSON.parse(el.textContent);
    } catch {
      return [];
    }
  }

  function setupBusinessTypeAutocomplete() {
    const inputEl = document.getElementById('business_type_search');
    const hiddenEl = document.getElementById('business_type');
    const listEl = document.getElementById('businessTypeSuggestions');
    const types = loadBusinessTypes();
    const maxItems = 8;
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

    function selectType(type) {
      inputEl.value = type.label;
      hiddenEl.value = type.value;
      closeSuggestions();
    }

    function filterTypes(query) {
      const q = normalizeText(query);
      if (!q) return types.slice(0, maxItems);

      const scored = types
        .map((type) => {
          const label = normalizeText(type.label);
          const value = normalizeText(type.value);
          const aliases = (type.aliases || []).map(normalizeText);
          const haystack = [label, value, ...aliases];
          const starts = haystack.some((text) => text.startsWith(q));
          const includes = haystack.some((text) => text.includes(q));
          if (!includes) return null;
          return { type, score: starts ? 0 : 1 };
        })
        .filter(Boolean)
        .sort((a, b) => a.score - b.score || a.type.label.localeCompare(b.type.label, 'pt-BR'));

      return scored.slice(0, maxItems).map((item) => item.type);
    }

    function renderSuggestions(suggestions) {
      listEl.innerHTML = '';
      activeIndex = -1;
      if (!suggestions.length) { closeSuggestions(); return; }

      suggestions.forEach((type) => {
        const li = document.createElement('li');
        li.className =
          'px-3 py-2 text-sm text-gray-700 cursor-pointer hover:bg-indigo-50 hover:text-indigo-700 dark:text-[#9897b3] dark:hover:bg-[#252340] dark:hover:text-[#e2e1f0] transition-colors';
        li.textContent = type.label;
        li.dataset.value = type.value;
        li.addEventListener('mousedown', (e) => {
          e.preventDefault();
          selectType(type);
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

    function showForQuery(query) {
      renderSuggestions(filterTypes(query));
    }

    function resolveExactMatch(query) {
      const q = normalizeText(query);
      if (!q) return null;
      const exact = types.filter((type) => {
        const label = normalizeText(type.label);
        const aliases = (type.aliases || []).map(normalizeText);
        return label === q || aliases.includes(q);
      });
      return exact.length === 1 ? exact[0] : null;
    }

    inputEl.addEventListener('input', () => {
      hiddenEl.value = '';
      inputEl.setCustomValidity('');
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => showForQuery(inputEl.value), 80);
    });

    inputEl.addEventListener('focus', () => {
      showForQuery(inputEl.value);
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
        const match = types.find((type) => type.value === el.dataset.value);
        if (match) selectType(match);
      } else if (e.key === 'Escape') {
        closeSuggestions();
      }
    });

    inputEl.addEventListener('blur', () => {
      setTimeout(() => {
        if (!hiddenEl.value) {
          const match = resolveExactMatch(inputEl.value);
          if (match) selectType(match);
        }
        closeSuggestions();
      }, 150);
    });

    inputEl.addEventListener('invalid', () => {
      if (!hiddenEl.value) {
        inputEl.setCustomValidity('Selecione um tipo de negócio da lista.');
      }
    });

    return {
      ensureSelected() {
        if (hiddenEl.value) return true;
        const match = resolveExactMatch(inputEl.value);
        if (match) {
          selectType(match);
          return true;
        }
        inputEl.setCustomValidity('Selecione um tipo de negócio da lista.');
        inputEl.reportValidity();
        showForQuery(inputEl.value);
        return false;
      },
    };
  }

  const businessTypeField = setupBusinessTypeAutocomplete();

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

  function buildRatingBadge(rating, total) {
    if (rating === null || rating === undefined) {
      return '<span class="text-gray-300 dark:text-[#3a3858] text-xs">—</span>';
    }
    const reviews = total !== null && total !== undefined ? total : 0;
    return `<span class="inline-flex items-center gap-1 text-xs font-medium text-gray-700 dark:text-[#c4c3da]">
      <svg class="w-3.5 h-3.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.368 2.447a1 1 0 00-.363 1.118l1.287 3.957c.3.921-.755 1.688-1.538 1.118l-3.368-2.447a1 1 0 00-1.176 0l-3.368 2.447c-.783.57-1.838-.197-1.538-1.118l1.287-3.957a1 1 0 00-.363-1.118L2.063 9.384c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69l1.286-3.957z"/>
      </svg>${rating.toFixed(1)} <span class="text-gray-400 dark:text-[#5c5b78]">(${reviews})</span>
    </span>`;
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

  function toWhatsAppUrl(phone) {
    if (!phone || phone === 'Não informado') return '';
    let digits = String(phone).replace(/\D/g, '');
    if (digits.length < 10) return '';
    if ((digits.length === 10 || digits.length === 11) && !digits.startsWith('55')) {
      digits = `55${digits}`;
    }
    // DDD + 8 digits (no leading 9): insert 9 only in the WhatsApp link
    if (digits.startsWith('55') && digits.length === 12) {
      digits = `${digits.slice(0, 4)}9${digits.slice(4)}`;
    }
    return `https://wa.me/${digits}`;
  }

  function buildWhatsAppButton(phone) {
    const url = toWhatsAppUrl(phone);
    if (!url) return '<span class="text-gray-300 dark:text-[#3a3858] text-xs">—</span>';
    return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer"
      class="inline-flex items-center gap-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold px-2.5 py-1.5 rounded-lg transition-colors whitespace-nowrap">
      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
      </svg>Enviar mensagem</a>`;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
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
        <td class="cell-phone px-4 py-3 text-gray-600 whitespace-nowrap">${escapeHtml(biz.phone)}${biz.phone && biz.phone !== 'Não informado' ? `<button onclick="copyPhone('${escapeHtml(biz.phone)}')" class="ml-1.5 inline-flex items-center justify-center w-5 h-5 text-gray-400 hover:text-brand-600 transition-colors align-middle flex-shrink-0" title="Copiar telefone"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg></button>` : ''}</td>
        <td class="px-4 py-3 text-center">${buildRatingBadge(biz.rating, biz.user_ratings_total)}</td>
        <td class="px-4 py-3 text-center">${buildWebsiteBadge(biz.has_website)}</td>
        <td class="px-4 py-3 text-center">${buildMapsLink(biz.maps_url)}</td>
        <td class="px-4 py-3 text-center">${buildWhatsAppButton(biz.phone)}</td>
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
    if (!businessTypeField.ensureSelected()) return;
    setLoading(true);

    const payload = {
      city: document.getElementById('city').value.trim(),
      neighborhood: document.getElementById('neighborhood').value.trim(),
      business_type: document.getElementById('business_type').value,
      quantity: parseInt(document.getElementById('quantity').value, 10),
      only_without_website: document.getElementById('only_without_website').checked,
      neighborhood_place_id: selectedNeighborhoodPlaceId,
      min_rating: parseFloat(document.getElementById('min_rating').value) || 0,
      min_reviews: parseInt(document.getElementById('min_reviews').value, 10) || 0,
    };

    try {
      const response = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.status === 401) {
        window.location.assign('/login?return_to=' + encodeURIComponent(window.location.pathname));
        return;
      }

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

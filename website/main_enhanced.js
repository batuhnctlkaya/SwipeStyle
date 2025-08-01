/**
 * SwipeStyle Frontend JavaScript
 * Basit ve temiz JavaScript kodu
 */

// Global dil değişkeni
let currentLanguage = 'tr';
let currentTheme = 'light';

// Autocomplete suggestions
const autocompleteData = {
    'tr': [
        { text: 'kablosuz kulaklık', icon: '🎧', category: 'Ses Teknolojisi' },
        { text: 'gaming laptop', icon: '💻', category: 'Bilgisayar' },
        { text: 'akıllı telefon', icon: '📱', category: 'Mobil' },
        { text: 'bluetooth hoparlör', icon: '🔊', category: 'Ses Teknolojisi' },
        { text: 'tablet', icon: '📱', category: 'Mobil' },
        { text: 'akıllı saat', icon: '⌚', category: 'Giyilebilir' },
        { text: 'drone', icon: '🚁', category: 'Hobi' },
        { text: 'kamera', icon: '📷', category: 'Fotoğraf' },
        { text: 'oyuncu klavyesi', icon: '⌨️', category: 'Gaming' },
        { text: 'gaming mouse', icon: '🖱️', category: 'Gaming' },
        { text: 'powerbank', icon: '🔋', category: 'Aksesuar' },
        { text: 'şarj kablosu', icon: '🔌', category: 'Aksesuar' },
        { text: 'wifi router', icon: '📶', category: 'Ağ' },
        { text: 'harici disk', icon: '💾', category: 'Depolama' },
        { text: 'mikrofon', icon: '🎤', category: 'Ses Teknolojisi' },
        { text: 'web kamerası', icon: '📹', category: 'Video' },
        { text: 'vr gözlük', icon: '🥽', category: 'Sanal Gerçeklik' },
        { text: 'akıllı tv', icon: '📺', category: 'Ev Eğlencesi' },
        { text: 'konsol', icon: '🎮', category: 'Gaming' },
        { text: 'fitness tracker', icon: '⌚', category: 'Sağlık' }
    ],
    'en': [
        { text: 'wireless headphones', icon: '🎧', category: 'Audio' },
        { text: 'gaming laptop', icon: '💻', category: 'Computer' },
        { text: 'smartphone', icon: '📱', category: 'Mobile' },
        { text: 'bluetooth speaker', icon: '🔊', category: 'Audio' },
        { text: 'tablet', icon: '📱', category: 'Mobile' },
        { text: 'smartwatch', icon: '⌚', category: 'Wearable' },
        { text: 'drone', icon: '🚁', category: 'Hobby' },
        { text: 'camera', icon: '📷', category: 'Photography' },
        { text: 'gaming keyboard', icon: '⌨️', category: 'Gaming' },
        { text: 'gaming mouse', icon: '🖱️', category: 'Gaming' },
        { text: 'power bank', icon: '🔋', category: 'Accessory' },
        { text: 'charging cable', icon: '🔌', category: 'Accessory' },
        { text: 'wifi router', icon: '📶', category: 'Network' },
        { text: 'external drive', icon: '💾', category: 'Storage' },
        { text: 'microphone', icon: '🎤', category: 'Audio' },
        { text: 'webcam', icon: '📹', category: 'Video' },
        { text: 'vr headset', icon: '🥽', category: 'Virtual Reality' },
        { text: 'smart tv', icon: '📺', category: 'Entertainment' },
        { text: 'gaming console', icon: '🎮', category: 'Gaming' },
        { text: 'fitness tracker', icon: '⌚', category: 'Health' }
    ]
};

// Autocomplete state
let currentAutocompleteIndex = -1;
let autocompleteVisible = false;
let autocompleteTimeout = null;

// Debounce function for autocomplete
function debounce(func, delay) {
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(autocompleteTimeout);
        autocompleteTimeout = setTimeout(() => func.apply(context, args), delay);
    };
}

// Tema değiştirme fonksiyonu
function changeTheme(theme) {
    currentTheme = theme;
    
    // HTML'e tema attribute'u ekle
    document.documentElement.setAttribute('data-theme', theme);
    
    // Theme switch'i güncelle
    document.querySelectorAll('.theme-switch').forEach(switch_el => {
        switch_el.dataset.theme = theme;
        if (theme === 'dark') {
            switch_el.classList.add('active');
        } else {
            switch_el.classList.remove('active');
        }
    });
    
    // LocalStorage'a kaydet
    localStorage.setItem('swipestyle-theme', theme);
}

// Dil değiştirme fonksiyonu
function changeLanguage(lang) {
    currentLanguage = lang;
    
    // Dil butonlarını güncelle
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.lang === lang) {
            btn.classList.add('active');
        }
    });
    
    // Tüm çevrilebilir elementleri güncelle
    document.querySelectorAll('[data-tr], [data-en]').forEach(element => {
        const trText = element.dataset.tr;
        const enText = element.dataset.en;
        
        if (lang === 'tr' && trText) {
            element.textContent = trText;
        } else if (lang === 'en' && enText) {
            element.textContent = enText;
        }
    });
    
    // Placeholder'ları güncelle
    document.querySelectorAll('[data-tr-placeholder], [data-en-placeholder]').forEach(element => {
        const trPlaceholder = element.dataset.trPlaceholder;
        const enPlaceholder = element.dataset.enPlaceholder;
        
        if (lang === 'tr' && trPlaceholder) {
            element.placeholder = trPlaceholder;
        } else if (lang === 'en' && enPlaceholder) {
            element.placeholder = enPlaceholder;
        }
    });
    
    // Kategorileri yeniden yükle
    loadCategories();
    
    // Autocomplete'i güncelle
    updateAutocompleteLanguage();
}

// Autocomplete functions
function initializeAutocomplete() {
    const input = document.getElementById('chatbox-input');
    const dropdown = document.getElementById('autocomplete-dropdown');
    
    if (!input || !dropdown) return;
    
    // Input events
    input.addEventListener('input', debounce(handleAutocompleteInput, 300));
    input.addEventListener('keydown', handleAutocompleteKeydown);
    input.addEventListener('focus', handleAutocompleteFocus);
    input.addEventListener('blur', handleAutocompleteBlur);
    
    // Document click to close dropdown
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            hideAutocomplete();
        }
    });
    
    // Handle window resize and scroll to reposition dropdown
    window.addEventListener('resize', function() {
        if (autocompleteVisible) {
            updateAutocompletePosition();
        }
    });
    
    window.addEventListener('scroll', function() {
        if (autocompleteVisible) {
            updateAutocompletePosition();
        }
    });
}

function updateAutocompletePosition() {
    const dropdown = document.getElementById('autocomplete-dropdown');
    const input = document.getElementById('chatbox-input');
    
    if (input && autocompleteVisible) {
        const inputRect = input.getBoundingClientRect();
        dropdown.style.top = `${inputRect.bottom}px`;
        dropdown.style.left = `${inputRect.left}px`;
        dropdown.style.width = `${inputRect.width}px`;
    }
}

function handleAutocompleteInput(e) {
    const query = e.target.value.trim().toLowerCase();
    const dropdown = document.getElementById('autocomplete-dropdown');
    
    if (query.length === 0) {
        hideAutocomplete();
        return;
    }
    
    // Show loading state briefly
    dropdown.innerHTML = '<div class="autocomplete-item"><span class="autocomplete-icon">⏳</span><span class="autocomplete-text">Loading...</span></div>';
    dropdown.classList.add('show');
    autocompleteVisible = true;
    
    getAutocompleteSuggestions(query).then(suggestions => {
        if (suggestions.length > 0) {
            showAutocompleteSuggestions(suggestions);
        } else {
            hideAutocomplete();
        }
    }).catch(error => {
        console.error('Autocomplete error:', error);
        hideAutocomplete();
    });
}

function handleAutocompleteKeydown(e) {
    const dropdown = document.getElementById('autocomplete-dropdown');
    const items = dropdown.querySelectorAll('.autocomplete-item');
    
    if (!autocompleteVisible || items.length === 0) return;
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            currentAutocompleteIndex = Math.min(currentAutocompleteIndex + 1, items.length - 1);
            updateAutocompleteHighlight(items);
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            currentAutocompleteIndex = Math.max(currentAutocompleteIndex - 1, -1);
            updateAutocompleteHighlight(items);
            break;
            
        case 'Enter':
            e.preventDefault();
            if (currentAutocompleteIndex >= 0 && currentAutocompleteIndex < items.length) {
                const selectedItem = items[currentAutocompleteIndex];
                const text = selectedItem.querySelector('.autocomplete-text').textContent;
                selectAutocompleteSuggestion(text);
            } else {
                handleChatboxEntry();
            }
            break;
            
        case 'Escape':
            hideAutocomplete();
            break;
    }
}

function handleAutocompleteFocus(e) {
    const query = e.target.value.trim().toLowerCase();
    if (query.length > 0) {
        getAutocompleteSuggestions(query).then(suggestions => {
            if (suggestions.length > 0) {
                showAutocompleteSuggestions(suggestions);
            }
        }).catch(error => {
            console.error('Autocomplete focus error:', error);
        });
    }
}

function handleAutocompleteBlur(e) {
    // Delay hiding to allow click on dropdown items
    setTimeout(() => {
        hideAutocomplete();
    }, 150);
}

function getAutocompleteSuggestions(query) {
    const data = autocompleteData[currentLanguage] || autocompleteData['tr'];
    const localSuggestions = data.filter(item => 
        item.text.toLowerCase().startsWith(query.toLowerCase())
    ).slice(0, 6);
    
    // If we have enough local suggestions, use them
    if (localSuggestions.length >= 3) {
        return Promise.resolve(localSuggestions);
    }
    
    // Otherwise, fetch from API as well
    return fetch(`/api/autocomplete?q=${encodeURIComponent(query)}&language=${currentLanguage}&limit=6`)
        .then(response => response.json())
        .then(data => {
            const apiSuggestions = (data.suggestions || []).filter(item => 
                item.text.toLowerCase().startsWith(query.toLowerCase())
            );
            
            // Combine local and API suggestions, removing duplicates
            const combined = [...localSuggestions];
            
            apiSuggestions.forEach(apiItem => {
                if (!combined.some(item => item.text.toLowerCase() === apiItem.text.toLowerCase())) {
                    combined.push(apiItem);
                }
            });
            
            return combined.slice(0, 6);
        })
        .catch(error => {
            console.error('Autocomplete API error:', error);
            return localSuggestions;
        });
}

function showAutocompleteSuggestions(suggestions) {
    const dropdown = document.getElementById('autocomplete-dropdown');
    const input = document.getElementById('chatbox-input');
    const query = input.value.trim();
    
    dropdown.innerHTML = '';
    currentAutocompleteIndex = -1;
    
    suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        
        // Highlight the matching portion
        const text = suggestion.text;
        const highlightedText = query.length > 0 ? 
            `<strong>${text.substring(0, query.length)}</strong>${text.substring(query.length)}` : 
            text;
        
        item.innerHTML = `
            <span class="autocomplete-icon">${suggestion.icon}</span>
            <span class="autocomplete-text">${highlightedText}</span>
            <span class="autocomplete-category">${suggestion.category}</span>
        `;
        
        item.addEventListener('click', () => {
            selectAutocompleteSuggestion(suggestion.text);
        });
        
        dropdown.appendChild(item);
    });
    
    // Calculate and set position
    if (input) {
        const inputRect = input.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        dropdown.style.position = 'fixed';
        dropdown.style.top = `${inputRect.bottom}px`;
        dropdown.style.left = `${inputRect.left}px`;
        dropdown.style.width = `${inputRect.width}px`;
        dropdown.style.zIndex = '99999';
        
        // Update input border radius for seamless connection
        input.style.borderRadius = '6px 6px 0 0';
        input.style.borderBottomColor = 'transparent';
    }
    
    dropdown.classList.add('show');
    autocompleteVisible = true;
}

function hideAutocomplete() {
    const dropdown = document.getElementById('autocomplete-dropdown');
    const input = document.getElementById('chatbox-input');
    
    dropdown.classList.remove('show');
    autocompleteVisible = false;
    currentAutocompleteIndex = -1;
    
    // Reset input border radius and border color
    if (input) {
        input.style.borderRadius = '6px';
        input.style.borderBottomColor = '';
    }
}

function updateAutocompleteHighlight(items) {
    items.forEach((item, index) => {
        if (index === currentAutocompleteIndex) {
            item.classList.add('highlighted');
        } else {
            item.classList.remove('highlighted');
        }
    });
}

function selectAutocompleteSuggestion(text) {
    const input = document.getElementById('chatbox-input');
    input.value = text;
    hideAutocomplete();
    input.focus();
}

function updateAutocompleteLanguage() {
    // Hide any open dropdown when language changes
    hideAutocomplete();
}

function handleChatboxEntry() {
    const input = document.getElementById('chatbox-input').value.trim();
    if (!input) {
        const alertMsg = currentLanguage === 'tr' ? 'Lütfen bir ürün yazın' : 'Please enter a product';
        alert(alertMsg);
        return;
    }
    
    // Arama butonunu devre dışı bırak
    const searchBtn = document.getElementById('chatbox-send');
    const originalText = searchBtn.innerHTML;
    const loadingText = currentLanguage === 'tr' ? '<i class="fas fa-spinner fa-spin"></i> Aranıyor...' : '<i class="fas fa-spinner fa-spin"></i> Searching...';
    searchBtn.innerHTML = loadingText;
    searchBtn.disabled = true;
    
    showLoadingScreen();
    
    // API çağrısı
    fetch('/api/create-category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category_name: input })
    })
    .then(res => res.json())
    .then(data => {
        hideLoadingScreen();
        
        // Butonu eski haline getir
        searchBtn.innerHTML = originalText;
        searchBtn.disabled = false;
        
        if (data.success && data.category) {
            category = data.category.name || data.category;
            step = 0;  // Start from 0 to include budget step
            answers = [];
            
            // Basit geçiş
            document.querySelector('.landing').style.display = 'none';
            document.getElementById('interaction').style.display = '';
            askAgent();
        } else {
            const errorMsg = data.error || (currentLanguage === 'tr' ? 'Aradığınız kategoriyi bulamadım. Lütfen başka bir şey deneyin.' : 'Could not find the category you are looking for. Please try something else.');
            alert(errorMsg);
        }
    })
    .catch(error => {
        console.error("Arama hatası:", error);
        hideLoadingScreen();
        
        // Butonu eski haline getir
        searchBtn.innerHTML = originalText;
        searchBtn.disabled = false;
        
        const errorMsg = currentLanguage === 'tr' ? "Bir hata oluştu, lütfen tekrar deneyin." : "An error occurred, please try again.";
        alert(errorMsg);
    });
}

let step = 0;
let category = null;
let answers = [];

const categoryIcons = {
    'Mouse': '🖱️',
    'Headphones': '🎧',
    'Phone': '📱',
    'Laptop': '💻',
    'Keyboard': '⌨️',
    'Monitor': '🖥️',
    'Speaker': '🔊',
    'Camera': '📷',
    'Tablet': '📱',
    'Smartwatch': '⌚'
};

// Kategori isimlerini çevir
const categoryTranslations = {
    'Mouse': { tr: 'Mouse', en: 'Mouse' },
    'Headphones': { tr: 'Kulaklık', en: 'Headphones' },
    'Phone': { tr: 'Telefon', en: 'Phone' },
    'Laptop': { tr: 'Laptop', en: 'Laptop' },
    'Keyboard': { tr: 'Klavye', en: 'Keyboard' },
    'Monitor': { tr: 'Monitör', en: 'Monitor' },
    'Speaker': { tr: 'Hoparlör', en: 'Speaker' },
    'Camera': { tr: 'Kamera', en: 'Camera' },
    'Tablet': { tr: 'Tablet', en: 'Tablet' },
    'Smartwatch': { tr: 'Akıllı Saat', en: 'Smartwatch' }
};

function getCategoryName(categoryName) {
    const translation = categoryTranslations[categoryName];
    if (translation) {
        return translation[currentLanguage] || categoryName;
    }
    return categoryName;
}

function loadCategories() {
    fetch('/api/categories')
        .then(res => res.json())
        .then(data => {
            const categories = data.categories || Object.keys(data);
            renderLanding(categories);
        })
        .catch(error => {
            console.error("Kategoriler yüklenirken hata:", error);
        });
}

function renderLanding(categories) {
    const grid = document.getElementById('category-cards');
    grid.innerHTML = '';
    
    categories.forEach(cat => {
        const card = document.createElement('div');
        card.className = 'category-card';
        
        // Handle both old format (string) and new format (object)
        const categoryName = typeof cat === 'string' ? cat : cat.name;
        const categoryEmoji = typeof cat === 'object' && cat.emoji ? cat.emoji : (categoryIcons[categoryName] || '🔍');
        
        card.onclick = () => startInteraction(categoryName);
        
        const icon = document.createElement('div');
        icon.className = 'category-icon';
        icon.textContent = categoryEmoji;
        
        const label = document.createElement('div');
        label.className = 'category-label';
        label.textContent = getCategoryName(categoryName);
        
        card.appendChild(icon);
        card.appendChild(label);
        grid.appendChild(card);
    });
    
    // Event listeners
    const chatboxSend = document.getElementById('chatbox-send');
    const chatboxInput = document.getElementById('chatbox-input');
    if (chatboxSend && chatboxInput) {
        chatboxSend.onclick = handleChatboxEntry;
        chatboxInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleChatboxEntry();
        });
    }
}

function startInteraction(selectedCategory) {
    category = selectedCategory;
    step = 0;  // Start from 0 to include budget step
    answers = [];
    
    // Basit geçiş
    document.querySelector('.landing').style.display = 'none';
    document.getElementById('interaction').style.display = '';
    askAgent();
}

function renderQuestion(question, options, emoji, isBudgetStep = false) {
    const interaction = document.getElementById('interaction');
    
    const questionDiv = interaction.querySelector('.question');
    const optionsDiv = interaction.querySelector('.options');
    
    if (!questionDiv || !optionsDiv) {
        console.error("Question or options div not found!");
        const errorMsg = currentLanguage === 'tr' ? 'Sayfa yapısında sorun var. Lütfen sayfayı yenileyin.' : 'There is a problem with the page structure. Please refresh the page.';
        document.querySelector('.error').textContent = errorMsg;
        return;
    }
    
    questionDiv.innerHTML = '';
    optionsDiv.innerHTML = '';
    
    // Soru başlığı
    const questionTitle = document.createElement('h2');
    questionTitle.innerHTML = `${emoji} ${question}`;
    questionDiv.appendChild(questionTitle);
    
    // Budget step: Render as dropdown
    if (isBudgetStep) {
        const selectContainer = document.createElement('div');
        selectContainer.className = 'budget-select-container';
        
        const select = document.createElement('select');
        select.className = 'budget-select';
        select.id = 'budget-select';
        
        // Add placeholder option
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = currentLanguage === 'tr' ? 'Bütçe aralığınızı seçin...' : 'Select your budget range...';
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        select.appendChild(placeholderOption);
        
        // Add budget options
        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt;
            select.appendChild(option);
        });
        
        // Add change event listener
        select.addEventListener('change', function() {
            if (this.value) {
                handleOption(this.value);
            }
        });
        
        selectContainer.appendChild(select);
        optionsDiv.appendChild(selectContainer);
    } else {
        // Regular questions: Render as buttons
        options.forEach(opt => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.textContent = opt;
            button.addEventListener('click', function() {
                handleOption(opt);
            });
            optionsDiv.appendChild(button);
        });
    }
    
    // Loading'i gizle
    const loadingDiv = interaction.querySelector('.loading');
    if (loadingDiv) loadingDiv.style.display = 'none';
    
    interaction.style.display = 'block';
}

function renderRecommendations(recs) {
    hideLoadingScreen();
    const recDiv = document.querySelector('.recommendations');
    
    const titleText = currentLanguage === 'tr' ? 'Önerilen Ürünler' : 'Recommended Products';
    
    let html = `
        <h2><i class="fas fa-star"></i> ${titleText}</h2>
        <div class="recommendations-grid">
    `;
    
    recs.forEach((r, index) => {
        // Debug: Log the product title to console
        console.log(`Product ${index + 1} title:`, r.title, 'Contains hyphen:', r.title?.includes('-'));
        
        let linkHtml = '';
        let url = r.link || '';
        if (url && !url.startsWith('http') && url.length > 5) {
            url = 'https://' + url.replace(/^(www\.)?/, '');
        }
        if (url && url.startsWith('http')) {
            const linkText = currentLanguage === 'tr' ? 'Satın Al' : 'Buy Now';
            linkHtml = `<a href="${url}" target="_blank" class="buy-link">
                <i class="fas fa-external-link-alt"></i> ${linkText}
            </a>`;
        }
        
        // Rating display
        let ratingHtml = '';
        if (r.rating) {
            const rating = parseFloat(r.rating);
            const fullStars = Math.floor(rating);
            const hasHalfStar = rating % 1 >= 0.5;
            const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
            
            let starsHtml = '';
            for (let i = 0; i < fullStars; i++) {
                starsHtml += '<i class="fas fa-star"></i>';
            }
            if (hasHalfStar) {
                starsHtml += '<i class="fas fa-star-half-alt"></i>';
            }
            for (let i = 0; i < emptyStars; i++) {
                starsHtml += '<i class="far fa-star"></i>';
            }
            
            const reviewsText = r.reviews ? 
                (currentLanguage === 'tr' ? `(${r.reviews} değerlendirme)` : `(${r.reviews} reviews)`) : '';
            
            ratingHtml = `
                <div class="product-rating">
                    <div class="stars">${starsHtml}</div>
                    <span class="rating-value">${rating.toFixed(1)}</span>
                    <span class="review-count">${reviewsText}</span>
                </div>
            `;
        }
        
        // Description display
        let descriptionHtml = '';
        if (r.description) {
            descriptionHtml = `<div class="product-description">${r.description}</div>`;
        }
        
        // Badge'leri ekle
        let badges = '';
        
        // Premium badge (her 3. ürün için)
        if (index % 3 === 0) {
            badges += '<div class="premium-badge">Premium</div>';
        }
        
        // İndirim badge (her 4. ürün için)
        if (index % 4 === 0) {
            const discountText = currentLanguage === 'tr' ? '%25 İndirim' : '%25 Discount';
            badges += `<div class="discount-badge">${discountText}</div>`;
        }
        
        // Oyunlaştırma badge (her 5. ürün için)
        if (index % 5 === 0) {
            const popularText = currentLanguage === 'tr' ? '🔥 Popüler' : '🔥 Popular';
            badges += `<div class="game-badge">${popularText}</div>`;
        }
        
        html += `
            <div class="recommendation-item">
                ${badges}
                <div class="recommendation-content">
                    <div class="product-image-container">
                        <img src="${r.image || 'https://via.placeholder.com/150x150?text=No+Image'}" 
                             alt="${r.name || r.title || 'Product'}" 
                             class="product-image"
                             loading="lazy"
                             onerror="this.src='https://via.placeholder.com/150x150?text=No+Image'">
                    </div>
                    <div class="product-details">
                        <div class="recommendation-name">${r.name || r.title || 'Product'}</div>
                        <div class="recommendation-price">${r.price}</div>
                        ${ratingHtml}
                        ${descriptionHtml}
                        ${linkHtml}
                    </div>
                </div>
            </div>
        `;
    });
    
    const backButtonText = currentLanguage === 'tr' ? 'Yeni Arama Yap' : 'New Search';
    
    html += `
        </div>
        <div class="back-section">
            <button id="back-to-categories" class="back-btn">
                <i class="fas fa-arrow-left"></i> ${backButtonText}
            </button>
        </div>
    `;
    
    recDiv.innerHTML = html;
    document.querySelector('.error').textContent = '';
    
    document.getElementById('back-to-categories').onclick = () => {
        resetToLanding();
    };
}

function resetToLanding() {
    const interaction = document.getElementById('interaction');
    const landing = document.querySelector('.landing');
    
    interaction.style.display = 'none';
    landing.style.display = '';
    
    // Reset all content
    document.querySelector('.recommendations').innerHTML = '';
        document.querySelector('.question').innerHTML = '';
        document.querySelector('.options').innerHTML = '';
        document.querySelector('.error').textContent = '';
    
    // Reset variables
        step = 0;
        category = null;
        answers = [];
    
    // Clear search input
    const searchInput = document.getElementById('chatbox-input');
    if (searchInput) searchInput.value = '';
}

function showLoadingScreen() {
    hideLoadingScreen();
    let loadingDiv = document.getElementById('custom-loading');
    if (!loadingDiv) {
        const loadingText = currentLanguage === 'tr' ? 'AI İşliyor...' : 'AI Processing...';
        const loadingSubtext = currentLanguage === 'tr' 
            ? 'Yapay zeka tercihlerinizi analiz ediyor ve size en uygun ürünleri buluyor.'
            : 'AI is analyzing your preferences and finding the most suitable products for you.';
        const resetText = currentLanguage === 'tr' ? 'Sıfırla' : 'Reset';
        
        loadingDiv = document.createElement('div');
        loadingDiv.id = 'custom-loading';
        loadingDiv.className = 'loading-container';
        loadingDiv.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">${loadingText}</div>
            <div class="loading-subtext">${loadingSubtext}</div>
            <div class="progress-container">
                <div class="progress-bar" id="ai-progress" style="width: 0%"></div>
            </div>
            <button class="emergency-reset" id="emergency-reset">
                <i class="fas fa-redo"></i> ${resetText}
            </button>
        `;
        
        // Acil durum sıfırlama butonu
        const resetButton = loadingDiv.querySelector('#emergency-reset');
        resetButton.onclick = () => {
            isRequestInProgress = false;
            hideLoadingScreen();
            resetToLanding();
        };
        
        document.body.appendChild(loadingDiv);
    }
    
    loadingDiv.style.display = 'flex';
    animateProgress();
}

function animateProgress() {
    const progressBar = document.getElementById('ai-progress');
    if (!progressBar) return;
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 3 + 1;
        if (progress > 90) progress = 90;
        
        progressBar.style.width = progress + '%';
        
        if (!document.getElementById('custom-loading') || 
            document.getElementById('custom-loading').style.display === 'none') {
            clearInterval(interval);
        }
    }, 200);
}

function hideLoadingScreen() {
    let loadingDiv = document.getElementById('custom-loading');
    if (loadingDiv) {
        const progressBar = document.getElementById('ai-progress');
        if (progressBar) {
            progressBar.style.width = '100%';
            setTimeout(() => {
                loadingDiv.style.display = 'none';
            }, 300);
        } else {
            loadingDiv.style.display = 'none';
        }
    }
}

let isRequestInProgress = false;

function handleOption(opt) {
    if (isRequestInProgress) {
        console.log("Request already in progress, ignoring click");
        return;
    }
    
    console.log("Option selected:", opt);
    
    try {
        isRequestInProgress = true;
        
        // Disable all option buttons
        const optionButtons = document.querySelectorAll('.option-btn');
        optionButtons.forEach(btn => {
            btn.disabled = true;
            btn.style.opacity = '0.5';
            btn.style.cursor = 'not-allowed';
        });
        
        // Seçimi görsel olarak göster
        const selectedButton = Array.from(optionButtons).find(btn => btn.textContent === opt);
        if (selectedButton) {
            selectedButton.style.backgroundColor = 'var(--cta-orange)';
            selectedButton.style.borderColor = 'var(--cta-orange)';
            selectedButton.style.color = 'white';
        }
        
        answers.push(opt);
        step++;
        
        document.querySelector('.error').textContent = '';
        
        console.log("İlerliyor: Adım", step, "Cevaplar:", answers);
        
        setTimeout(function() {
            askAgent();
        }, 300);
    } catch(e) {
        console.error("handleOption'da hata:", e);
        isRequestInProgress = false;
        const errorMsg = currentLanguage === 'tr' ? 'İşlem sırasında bir hata oluştu. Lütfen sayfayı yenileyin.' : 'An error occurred during processing. Please refresh the page.';
        document.querySelector('.error').textContent = errorMsg;
    }
}

function askAgent() {
    console.log(`Soru soruluyor: Step ${step}, Category ${category}, Answers:`, answers);
    
    document.querySelector('.error').textContent = '';
    
    const loadingElement = document.querySelector('.loading');
    if (loadingElement) {
        loadingElement.style.display = 'block';
        const loadingText = currentLanguage === 'tr' ? '<i class="fas fa-spinner fa-spin"></i> Yükleniyor...' : '<i class="fas fa-spinner fa-spin"></i> Loading...';
        loadingElement.innerHTML = loadingText;
    }
    
    console.log("İstek başlatılıyor:", {
        step: step,
        category: category,
        answers: answers,
        isRequestInProgress: isRequestInProgress
    });
    
    let specs = window.currentSpecs && window.currentSpecs[category] ? window.currentSpecs[category] : [];
    if (step > specs.length) {
        showLoadingScreen();
    }
    
    const timeoutId = setTimeout(() => {
        if (isRequestInProgress) {
            console.log("Zaman aşımı oluştu!");
            isRequestInProgress = false;
            hideLoadingScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            const timeoutMsg = currentLanguage === 'tr' ? 'İstek zaman aşımına uğradı. AI analizi uzun sürdü, lütfen tekrar deneyin.' : 'Request timed out. AI analysis took too long, please try again.';
            document.querySelector('.error').textContent = timeoutMsg;
        }
    }, 45000);
    
    fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            step: step, 
            category: category, 
            answers: answers,
            language: currentLanguage
        })
    })
    .then(res => {
        console.log("Sunucu yanıt verdi:", res.status);
        if (!res.ok) {
            throw new Error(`HTTP hata: ${res.status} ${res.statusText}`);
        }
        return res.json();
    })
    .then(data => {
        clearTimeout(timeoutId);
        isRequestInProgress = false;
        console.log("Sunucudan gelen yanıt:", data);
        
        console.log("Response has question:", !!data.question);
        console.log("Response has options:", !!data.options);
        console.log("Response has recommendations:", !!data.recommendations);
        console.log("Response has error:", !!data.error);
        console.log("Response keys:", Object.keys(data));
        
        if (data.question && data.options) {
            hideLoadingScreen();
            window.currentQuestionTooltip = data.tooltip || null;
            renderQuestion(data.question, data.options, data.emoji || '🔍', data.is_budget_step || false);
        } else if (data.recommendations) {
            renderRecommendations(data.recommendations);
        } else if (data.categories) {
            renderLanding(data.categories);
        } else if (data.error) {
            hideLoadingScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            document.querySelector('.error').textContent = data.error;
        } else {
            console.error('Beklenmeyen yanıt formatı:', data);
            hideLoadingScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            const unexpectedMsg = currentLanguage === 'tr' ? 'Beklenmeyen bir yanıt alındı. Lütfen sayfayı yenileyin.' : 'An unexpected response was received. Please refresh the page.';
            document.querySelector('.error').textContent = unexpectedMsg;
        }
    })
    .catch(err => {
        clearTimeout(timeoutId);
        isRequestInProgress = false;
        
        hideLoadingScreen();
        if (loadingElement) loadingElement.style.display = 'none';
        const errorMsg = currentLanguage === 'tr' ? 'Sunucuya erişilemiyor: ' : 'Cannot access server: ';
        document.querySelector('.error').textContent = errorMsg + err.message;
        console.error('Hata:', err);
    });
}

window.onload = () => {
    console.log("SwipeStyle uygulaması başlatılıyor...");
    
    // Tema tercihini localStorage'dan yükle
    const savedTheme = localStorage.getItem('swipestyle-theme') || 'light';
    changeTheme(savedTheme);
    
    // Dil değiştirme event listener'ları
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const lang = this.dataset.lang;
            changeLanguage(lang);
        });
    });
    
    // Tema değiştirme event listener'ları
    document.querySelectorAll('.theme-switch').forEach(switch_el => {
        switch_el.addEventListener('click', function() {
            const currentTheme = this.dataset.theme;
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Switch'i güncelle
            this.dataset.theme = newTheme;
            this.classList.toggle('active');
            
            // Temayı değiştir
            changeTheme(newTheme);
        });
    });
    
    // CSS ekle
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .recommendations-grid {
                display: grid;
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .recommendation-content {
                display: flex;
                align-items: flex-start;
                gap: 15px;
                padding: 15px;
                border-radius: 10px;
                background: var(--bg-light);
                border: 1px solid var(--border-light);
                transition: all 0.3s ease;
            }
            
            .recommendation-content:hover {
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            
            .product-image-container {
                flex-shrink: 0;
                width: 100px;
                height: 100px;
                border-radius: 8px;
                overflow: hidden;
                background: #f8f9fa;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .product-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }
            
            .product-image:hover {
                transform: scale(1.05);
            }
            
            .product-details {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .recommendation-name {
                font-weight: 600;
                color: var(--text-dark);
                font-size: 1.1rem;
                line-height: 1.3;
            }
            
            .recommendation-price {
                color: var(--primary-blue);
                font-weight: 500;
                font-size: 1.2rem;
            }
            
            .product-rating {
                display: flex;
                align-items: center;
                gap: 8px;
                margin: 5px 0;
            }
            
            .stars {
                color: #ffd700;
                font-size: 0.9rem;
            }
            
            .rating-value {
                font-weight: 500;
                color: var(--text-dark);
                font-size: 0.9rem;
            }
            
            .review-count {
                color: var(--text-muted);
                font-size: 0.8rem;
            }
            
            .product-description {
                color: var(--text-muted);
                font-size: 0.9rem;
                line-height: 1.4;
                margin: 5px 0;
            }
            
            .buy-link {
                background: var(--cta-orange);
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
                text-decoration: none;
                font-size: 0.9rem;
                font-weight: 500;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                align-self: flex-start;
                margin-top: 8px;
            }
            
            .buy-link:hover {
                background: var(--cta-orange-hover);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
            }
            
            .back-section {
                text-align: center;
                margin-top: 20px;
            }
            
            /* Mobile responsive */
            @media (max-width: 768px) {
                .recommendation-content {
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                }
                
                .product-image-container {
                    width: 120px;
                    height: 120px;
                }
                
                .product-details {
                    align-items: center;
                }
            }
        </style>
    `);
    
    // Get categories from backend
    fetch('/api/categories')
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            console.log("Kategoriler yüklendi:", data);
            
            const categories = data.categories || Object.keys(data);
            window.currentSpecs = {};
            
            // Handle enhanced response format
            if (Array.isArray(categories)) {
                categories.forEach(cat => {
                    const categoryName = typeof cat === 'string' ? cat : cat.name;
                    window.currentSpecs[categoryName] = cat.specs || [];
                });
            } else {
                for (const cat of categories) {
                    window.currentSpecs[cat] = data[cat]?.specs || [];
                }
            }
            
            renderLanding(categories);
            
            const chatboxSend = document.getElementById('chatbox-send');
            const chatboxInput = document.getElementById('chatbox-input');
            
            if (chatboxSend && chatboxInput) {
                chatboxSend.onclick = handleChatboxEntry;
                chatboxInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') handleChatboxEntry();
                });
            }
            
            // Initialize autocomplete
            initializeAutocomplete();
            
            console.log("SwipeStyle başarıyla başlatıldı");
        })
        .catch(error => {
            console.error("Kategoriler yüklenirken hata oluştu:", error);
            const errorMsg = currentLanguage === 'tr' ? "Kategoriler yüklenemedi. Lütfen sayfayı yenileyin." : "Categories could not be loaded. Please refresh the page.";
            document.querySelector('.error').textContent = errorMsg;
        });
};

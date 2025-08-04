/**
 * SwipeStyle Frontend JavaScript
 * Basit ve temiz JavaScript kodu
 */

// Global dil değişkeni
let currentLanguage = 'tr';
let currentTheme = 'light';

// Otomatik tamamlama için global değişkenler
let autocompleteData = [];
let selectedAutocompleteIndex = -1;

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
                fetch('/detect_category', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: input })
                })
                .then(res => res.json())
    .then(data => {
        hideLoadingScreen();
        
        // Butonu eski haline getir
        searchBtn.innerHTML = originalText;
        searchBtn.disabled = false;
        
        if (data.category) {
            category = data.category;
                        step = 1;
                        answers = [];
            
            // Basit geçiş
                        document.querySelector('.landing').style.display = 'none';
                        document.getElementById('interaction').style.display = '';
                        askAgent();
                    } else {
            const errorMsg = currentLanguage === 'tr' ? 'Aradığınız kategoriyi bulamadım. Lütfen başka bir şey deneyin.' : 'Could not find the category you are looking for. Please try something else.';
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
    'Mouse': 'fas fa-mouse',
    'Headphones': 'fas fa-headphones',
    'Phone': 'fas fa-mobile-alt',
    'Laptop': 'fas fa-laptop',
    'Keyboard': 'fas fa-keyboard',
    'Monitor': 'fas fa-desktop',
    'Speaker': 'fas fa-volume-up',
    'Camera': 'fas fa-camera',
    'Tablet': 'fas fa-tablet-alt',
    'Smartwatch': 'fas fa-clock'
};

// --- Akıllı Arama & Filtreleme Özelliği ---
// Not: HTML kısmını main.html dosyasına eklemelisin (bkz. açıklama)

// Örnek teknolojik ürün verisi (backend'den de çekilebilir)
const products = [
  { name: "Mouse", color: "siyah", size: "M", price: 399, rating: 4.6 },
  { name: "Laptop", color: "gri", size: "L", price: 15999, rating: 4.8 },
  { name: "Telefon", color: "mavi", size: "M", price: 10999, rating: 4.7 },
  { name: "Kulaklık", color: "siyah", size: "S", price: 799, rating: 4.3 },
  { name: "Monitör", color: "beyaz", size: "L", price: 2999, rating: 4.5 },
  { name: "Klavye", color: "siyah", size: "M", price: 599, rating: 4.2 },
  { name: "Tablet", color: "gri", size: "M", price: 4999, rating: 4.4 },
  { name: "Kamera", color: "siyah", size: "S", price: 3499, rating: 4.1 },
  { name: "Hoparlör", color: "kırmızı", size: "S", price: 699, rating: 4.0 },
  { name: "Akıllı Saat", color: "siyah", size: "S", price: 1999, rating: 4.6 }
];

// Ürünleri ekrana bas
function displayProducts(filtered) {
  const productList = document.getElementById("product-list");
  if (!productList) return;
  productList.innerHTML = "";
  filtered.forEach(p => {
    const div = document.createElement("div");
    div.className = "product";
    div.textContent = `${p.name} | Renk: ${p.color} | Beden: ${p.size} | ₺${p.price} | ⭐${p.rating}`;
    productList.appendChild(div);
  });
}

// Filtreleme fonksiyonu
function filterProducts() {
  const inputEl = document.getElementById("product-search-input");
  const colorEl = document.getElementById("color-filter");
  const sizeEl = document.getElementById("size-filter");
  const ratingEl = document.getElementById("rating-filter");
  if (!inputEl || !colorEl || !sizeEl || !ratingEl) return;
  const input = inputEl.value.toLowerCase();
  const color = colorEl.value;
  const size = sizeEl.value;
  const rating = parseFloat(ratingEl.value) || 0;

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(input) &&
    (color === "" || p.color === color) &&
    (size === "" || p.size === size) &&
    p.rating >= rating
  );
  displayProducts(filtered);
}

// Otomatik tamamlama
function setupSmartSearchEvents() {
  const inputEl = document.getElementById("product-search-input");
  const suggestionsDiv = document.getElementById("product-suggestions");
  if (!inputEl || !suggestionsDiv) return;
  inputEl.addEventListener("input", () => {
    const input = inputEl.value.toLowerCase();
    const matched = products
      .map(p => p.name)
      .filter(name => name.toLowerCase().startsWith(input));
    suggestionsDiv.innerHTML = matched.length > 0 ? matched.join(", ") : "";
    filterProducts();
  });
}

function setupFilterEvents() {
  const colorEl = document.getElementById("color-filter");
  const sizeEl = document.getElementById("size-filter");
  const ratingEl = document.getElementById("rating-filter");
  if (colorEl) colorEl.addEventListener("change", filterProducts);
  if (sizeEl) sizeEl.addEventListener("change", filterProducts);
  if (ratingEl) ratingEl.addEventListener("change", filterProducts);
}

// Sayfa yüklendiğinde smart search alanı varsa başlat
window.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById("product-search-input")) {
    setupSmartSearchEvents();
    setupFilterEvents();
    displayProducts(products);
  }
});

// Açıklama: HTML tarafına şunu eklemelisin (örnek):
// <div class="smart-search">
//   <input type="text" id="product-search-input" placeholder="Ürün Ara (örn: ka)">
//   <select id="color-filter"> ... </select>
//   <select id="size-filter"> ... </select>
//   <select id="rating-filter"> ... </select>
//   <div id="product-suggestions"></div>
// </div>
// <div id="product-list"></div>

// Otomatik tamamlama verileri
const autocompleteSuggestions = {
    'k': [
        { text: 'Kulaklık', icon: 'fas fa-headphones', category: 'Headphones' },
        { text: 'Klavye', icon: 'fas fa-keyboard', category: 'Keyboard' },
        { text: 'Kamera', icon: 'fas fa-camera', category: 'Camera' },
        { text: 'Klima', icon: 'fas fa-snowflake', category: 'Air Conditioner' },
        { text: 'Kettle', icon: 'fas fa-mug-hot', category: 'Kitchen' },
        { text: 'Konsol', icon: 'fas fa-gamepad', category: 'Gaming' }
    ],
    'kl': [
        { text: 'Klima', icon: 'fas fa-snowflake', category: 'Air Conditioner' },
        { text: 'Klavye', icon: 'fas fa-keyboard', category: 'Keyboard' }
    ],
    'kli': [
        { text: 'Klima', icon: 'fas fa-snowflake', category: 'Air Conditioner' }
    ],
    'klim': [
        { text: 'Klima', icon: 'fas fa-snowflake', category: 'Air Conditioner' }

    ],
    'l': [
        { text: 'Laptop', icon: 'fas fa-laptop', category: 'Laptop' }
    ],
    'la': [
        { text: 'Laptop', icon: 'fas fa-laptop', category: 'Laptop' }
    ],
    'lap': [
        { text: 'Laptop', icon: 'fas fa-laptop', category: 'Laptop' }
    ],
    'lapt': [
        { text: 'Laptop', icon: 'fas fa-laptop', category: 'Laptop' }
    ],
    'lapto': [
        { text: 'Laptop', icon: 'fas fa-laptop', category: 'Laptop' }
    ],
    'laptop': [
        { text: 'Laptop Gaming', icon: 'fas fa-laptop', category: 'Laptop' },
        { text: 'Laptop Ultrabook', icon: 'fas fa-laptop', category: 'Laptop' },
        { text: 'Laptop 2 in 1', icon: 'fas fa-laptop', category: 'Laptop' },
        { text: 'Laptop MacBook', icon: 'fas fa-laptop', category: 'Laptop' },
        { text: 'Laptop Dell', icon: 'fas fa-laptop', category: 'Laptop' },
        { text: 'Laptop HP', icon: 'fas fa-laptop', category: 'Laptop' },
        { text: 'Laptop Lenovo', icon: 'fas fa-laptop', category: 'Laptop' },
        { text: 'Laptop Asus', icon: 'fas fa-laptop', category: 'Laptop' }
    ],
    'm': [
        { text: 'Mouse', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Gaming', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Kablosuz', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Bluetooth', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Logitech', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Razer', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse SteelSeries', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Corsair', icon: 'fas fa-mouse', category: 'Mouse' }
    ],
    'mo': [
        { text: 'Mouse', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Gaming', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Kablosuz', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Bluetooth', icon: 'fas fa-mouse', category: 'Mouse' }
    ],
    'mou': [
        { text: 'Mouse', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Gaming', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Kablosuz', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Bluetooth', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Logitech', icon: 'fas fa-mouse', category: 'Mouse' }
    ],
    'mous': [
        { text: 'Mouse', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Gaming', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Kablosuz', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Bluetooth', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Logitech', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Razer', icon: 'fas fa-mouse', category: 'Mouse' }
    ],
    'mouse': [
        { text: 'Mouse Gaming', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Kablosuz', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Bluetooth', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Logitech', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Razer', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse SteelSeries', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse Corsair', icon: 'fas fa-mouse', category: 'Mouse' },
        { text: 'Mouse HyperX', icon: 'fas fa-mouse', category: 'Mouse' }
    ],
    't': [
        { text: 'Telefon', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Tablet', icon: 'fas fa-tablet-alt', category: 'Tablet' },
        { text: 'TV', icon: 'fas fa-tv', category: 'TV' },
        { text: 'Televizyon', icon: 'fas fa-tv', category: 'TV' },
        { text: 'Telefon iPhone', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Samsung', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Xiaomi', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Huawei', icon: 'fas fa-mobile-alt', category: 'Phone' }
    ],
    'te': [
        { text: 'Telefon', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Tablet', icon: 'fas fa-tablet-alt', category: 'Tablet' },
        { text: 'TV', icon: 'fas fa-tv', category: 'TV' },
        { text: 'Televizyon', icon: 'fas fa-tv', category: 'TV' }
    ],
    'tel': [
        { text: 'Telefon', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon iPhone', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Samsung', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Xiaomi', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Huawei', icon: 'fas fa-mobile-alt', category: 'Phone' }
    ],
    'tele': [
        { text: 'Telefon', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon iPhone', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Samsung', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Xiaomi', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Huawei', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon OnePlus', icon: 'fas fa-mobile-alt', category: 'Phone' }
    ],
    'telef': [
        { text: 'Telefon', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon iPhone', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Samsung', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Xiaomi', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Huawei', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon OnePlus', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Google', icon: 'fas fa-mobile-alt', category: 'Phone' }
    ],
    'telefo': [
        { text: 'Telefon', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon iPhone', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Samsung', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Xiaomi', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Huawei', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon OnePlus', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Google', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Nokia', icon: 'fas fa-mobile-alt', category: 'Phone' }
    ],
    'telefon': [
        { text: 'Telefon iPhone', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Samsung', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Xiaomi', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Huawei', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon OnePlus', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Google', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Nokia', icon: 'fas fa-mobile-alt', category: 'Phone' },
        { text: 'Telefon Sony', icon: 'fas fa-mobile-alt', category: 'Phone' }
    ]
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

// Otomatik tamamlama fonksiyonları
function handleAutocomplete() {
    const input = document.getElementById('chatbox-input');
    const dropdown = document.getElementById('autocomplete-dropdown');
    const query = input.value.toLowerCase().trim();
    
    if (query.length < 1) {
        hideAutocomplete();
        return;
    }
    
    // Önerileri bul
    const suggestions = getAutocompleteSuggestions(query);
    
    if (suggestions.length > 0) {
        showAutocompleteSuggestions(suggestions);
    } else {
        hideAutocomplete();
    }
}

function getAutocompleteSuggestions(query) {
    const suggestions = [];
    if (!query) return suggestions;

    // Regex ile anahtar eşleşmesi (başlangıç veya tam eşleşme)
    const keyRegex = new RegExp('^' + query, 'i');
    Object.keys(autocompleteSuggestions).forEach(key => {
        if (keyRegex.test(key)) {
            autocompleteSuggestions[key].forEach(suggestion => {
                if (!suggestions.some(s => s.text === suggestion.text)) {
                    suggestions.push(suggestion);
                }
            });
        }
    });

    // Regex ile ürün adında geçenler (herhangi bir yerde)
    const textRegex = new RegExp(query, 'i');
    Object.values(autocompleteSuggestions).forEach(categorySuggestions => {
        categorySuggestions.forEach(suggestion => {
            if (textRegex.test(suggestion.text) && !suggestions.some(s => s.text === suggestion.text)) {
                suggestions.push(suggestion);
            }
        });
    });

    return suggestions.slice(0, 8); // Maksimum 8 öneri
}

function showAutocompleteSuggestions(suggestions) {
    const dropdown = document.getElementById('autocomplete-dropdown');
    
    dropdown.innerHTML = '';
    autocompleteData = suggestions; // Global değişkene ata
    
    suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.setAttribute('data-index', index);
        item.setAttribute('data-category', suggestion.category);
        
        item.innerHTML = `
            <span>${suggestion.text}</span>
            <i class="${suggestion.icon} icon" title="${suggestion.category}"></i>
        `;
        
        item.addEventListener('click', () => {
            selectAutocompleteItem(suggestion);
        });
        
        item.addEventListener('mouseenter', () => {
            selectAutocompleteIndex(index);
        });
        
        // Add subtle animation delay for each item
        item.style.animationDelay = `${index * 0.05}s`;
        item.style.animation = 'fadeInUp 0.3s ease forwards';
        
        dropdown.appendChild(item);
    });
    
    dropdown.style.display = 'block';
    selectedAutocompleteIndex = -1;
}

function hideAutocomplete() {
    const dropdown = document.getElementById('autocomplete-dropdown');
    dropdown.style.display = 'none';
    selectedAutocompleteIndex = -1;
}

function selectAutocompleteIndex(index) {
    const items = document.querySelectorAll('.autocomplete-item');
    
    // Önceki seçimi temizle
    items.forEach(item => item.classList.remove('selected'));
    
    if (index >= 0 && index < items.length) {
        items[index].classList.add('selected');
        selectedAutocompleteIndex = index;
    }
}

function selectAutocompleteItem(suggestion) {
    const input = document.getElementById('chatbox-input');
    input.value = suggestion.text;
    hideAutocomplete();
    
    // Otomatik olarak arama yap
    handleChatboxEntry();
}

function handleAutocompleteKeydown(e) {
    const dropdown = document.getElementById('autocomplete-dropdown');
    const items = document.querySelectorAll('.autocomplete-item');
    
    if (dropdown.style.display === 'none') return;
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            selectedAutocompleteIndex = Math.min(selectedAutocompleteIndex + 1, items.length - 1);
            selectAutocompleteIndex(selectedAutocompleteIndex);
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            selectedAutocompleteIndex = Math.max(selectedAutocompleteIndex - 1, -1);
            selectAutocompleteIndex(selectedAutocompleteIndex);
            break;
            
        case 'Enter':
            e.preventDefault();
            if (selectedAutocompleteIndex >= 0 && selectedAutocompleteIndex < items.length) {
                const selectedItem = items[selectedAutocompleteIndex];
                const suggestion = autocompleteData[selectedAutocompleteIndex];
                if (suggestion) {
                    selectAutocompleteItem(suggestion);
                }
            } else {
                handleChatboxEntry();
            }
            break;
            
        case 'Escape':
            hideAutocomplete();
            break;
    }
}

function getCategoryName(categoryName) {
    const translation = categoryTranslations[categoryName];
    if (translation) {
        return translation[currentLanguage] || categoryName;
    }
    return categoryName;
}

function loadCategories() {
    fetch('/categories')
        .then(res => res.json())
        .then(data => {
            const categories = Object.keys(data);
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
        card.onclick = () => startInteraction(cat);
        
        const icon = document.createElement('div');
        icon.className = 'category-icon';
        
        // Font Awesome ikonu için
        const iconElement = document.createElement('i');
        iconElement.className = categoryIcons[cat] || 'fas fa-search';
        icon.appendChild(iconElement);
        
        const label = document.createElement('div');
        label.className = 'category-label';
        label.textContent = getCategoryName(cat);
        
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
    step = 1;
    answers = [];
    
    // Basit geçiş
    document.querySelector('.landing').style.display = 'none';
    document.getElementById('interaction').style.display = '';
    askAgent();
}

function renderQuestion(question, options, emoji) {
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
    
    // Seçenekleri oluştur
    options.forEach(opt => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        button.textContent = opt;
        button.addEventListener('click', function() {
            handleOption(opt);
        });
        optionsDiv.appendChild(button);
    });
    
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
                    <div class="recommendation-name">${r.name}</div>
                    <div class="recommendation-price">${r.price}</div>
                    ${linkHtml}
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
    
    fetch('/ask', {
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
            renderQuestion(data.question, data.options, data.emoji || '🔍');
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
    
    // Otomatik tamamlama için input event listener
    const searchInput = document.getElementById('chatbox-input');
    searchInput.addEventListener('input', handleAutocomplete);
    searchInput.addEventListener('keydown', handleAutocompleteKeydown);
    searchInput.addEventListener('blur', hideAutocomplete);
    
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
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .recommendation-name {
                font-weight: 600;
                color: var(--text-dark);
                flex: 1;
            }
            
            .recommendation-price {
                color: var(--primary-blue);
                font-weight: 500;
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
        </style>
    `);
    
    // Get categories from backend
    fetch('/categories')
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            console.log("Kategoriler yüklendi:", Object.keys(data));
            
            const categories = Object.keys(data);
            window.currentSpecs = {};
            
            for (const cat of categories) {
                window.currentSpecs[cat] = data[cat].specs || [];
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
            
            console.log("SwipeStyle başarıyla başlatıldı");
        })
        .catch(error => {
            console.error("Kategoriler yüklenirken hata oluştu:", error);
            const errorMsg = currentLanguage === 'tr' ? "Kategoriler yüklenemedi. Lütfen sayfayı yenileyin." : "Categories could not be loaded. Please refresh the page.";
            document.querySelector('.error').textContent = errorMsg;
        });
    
    // Akıllı arama bileşenini oluştur
    const smartSearchHtml = `
        <div class="smart-search">
          <input type="text" id="product-search-input" placeholder="Ürün Ara (örn: ka)">
          <select id="color-filter">
            <option value="">Renk</option>
            <option value="kırmızı">Kırmızı</option>
            <option value="siyah">Siyah</option>
            <option value="mavi">Mavi</option>
          </select>
          <select id="size-filter">
            <option value="">Beden</option>
            <option value="S">S</option>
            <option value="M">M</option>
            <option value="L">L</option>
          </select>
          <select id="rating-filter">
            <option value="">Puan</option>
            <option value="4">4+ Yıldız</option>
            <option value="3">3+ Yıldız</option>
          </select>
          <div id="product-suggestions"></div>
        </div>
        <div id="product-list"></div>
    `;
    
    document.getElementById('smart-search-container').innerHTML = smartSearchHtml;

};

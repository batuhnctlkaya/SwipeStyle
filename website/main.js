/**
 * SwipeStyle Frontend JavaScript
 * Basit ve temiz JavaScript kodu
 */

// Global dil değişkeni
let currentLanguage = 'tr';
let currentTheme = 'light';
let currentCategory = ''; // Global kategori değişkeni

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
    
    // Modern AI creation screen göster
    showAICreationScreen();
    
    // API çağrısı
    fetch('/detect_category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
    })
    .then(res => res.json())
    .then(data => {
        hideAICreationScreen();
        
        if (data.category) {
            category = data.category;
            currentCategory = data.category; // Global kategoriyi güncelle
            step = 1;
            answers = [];
            
            // Modern geçiş
            document.querySelector('.landing').style.display = 'none';
            document.getElementById('interaction').style.display = '';
            askAgent();
        } else {
            showErrorScreen();
        }
    })
    .catch(error => {
        console.error("Arama hatası:", error);
        hideAICreationScreen();
        showErrorScreen();
    });
}

let step = 0;
let category = null;
let answers = [];

// Mevcut kategoriyi döndüren yardımcı fonksiyon
function getCurrentCategory() {
    return currentCategory || category || '';
}

// Ürün başlığından marka çıkarma fonksiyonu
function extractBrand(productTitle) {
    const title = productTitle.toLowerCase();
    const brandKeywords = [
        'sony', 'bose', 'apple', 'samsung', 'lg', 'sennheiser', 'beats', 
        'xiaomi', 'huawei', 'oppo', 'oneplus', 'realme', 'vivo', 'iphone',
        'airpods', 'galaxy', 'pixel', 'redmi', 'poco', 'honor',
        'jbl', 'marshall', 'audio-technica', 'beyerdynamic', 'akg',
        'skullcandy', 'plantronics', 'jabra', 'razer', 'steelseries',
        'hyperx', 'corsair', 'logitech', 'asus', 'msi', 'acer', 'hp',
        'dell', 'lenovo', 'macbook', 'thinkpad', 'pavilion', 'inspiron'
    ];
    
    for (const brand of brandKeywords) {
        if (title.includes(brand)) {
            return brand;
        }
    }
    return null;
}

// Ürün başlığından model çıkarma fonksiyonu  
function extractModel(productTitle) {
    const title = productTitle.toLowerCase();
    
    // Model pattern'leri (sayı kombinasyonları)
    const modelPatterns = [
        /\b\d{1,2}[a-z]*\b/g,  // 12, 12a, 13pro gibi
        /\b[a-z]+\s*\d+[a-z]*\b/g,  // pro max 12, air 3 gibi
        /\b\d+\s*[a-z]+\b/g  // 12 pro, 3 max gibi
    ];
    
    for (const pattern of modelPatterns) {
        const matches = title.match(pattern);
        if (matches && matches.length > 0) {
            return matches[0];
        }
    }
    return null;
}

const categoryIcons = {
    'Headphones': 'fas fa-headphones',
    'Klima': 'fas fa-snowflake',
    'Tire': 'fas fa-circle',
    'Television': 'fas fa-tv',
    'Telefon': 'fas fa-mobile-alt'
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
    currentCategory = selectedCategory; // Global kategoriyi güncelle
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
    console.log("🎯 renderRecommendations called");
    console.log("📊 Recommendations type:", typeof recs);
    console.log("📊 Is array:", Array.isArray(recs));
    console.log("📊 Length:", recs ? recs.length : 'null/undefined');
    console.log("📊 Full data:", JSON.stringify(recs, null, 2));
    
    // Loading ekranlarını gizle
    hideAICreationScreen();
    const loadingElement = document.querySelector('.loading');
    if (loadingElement) loadingElement.style.display = 'none';
    
    const recDiv = document.querySelector('.recommendations');
    
    const titleText = currentLanguage === 'tr' ? 'Önerilen Ürünler' : 'Recommended Products';
    
    // Check if recs is valid
    if (!recs || !Array.isArray(recs) || recs.length === 0) {
        console.error("❌ No valid recommendations to render");
        recDiv.innerHTML = `
            <div class="error-message">
                <h3>Ürün bulunamadı</h3>
                <p>Seçimlerinizle eşleşen ürün bulunamadı. Lütfen farklı seçenekler deneyin.</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <h2><i class="fas fa-star"></i> ${titleText}</h2>
        <div class="recommendations-grid">
    `;
    
    recs.forEach((r, index) => {
        console.log(`📦 Processing recommendation ${index}:`, r);
        console.log(`📦 Recommendation keys:`, Object.keys(r));
        
        // Modern search engine format adaptasyonu
        const productTitle = r.title || r.name || 'Ürün';
        const productPrice = r.price ? 
            (typeof r.price === 'object' ? r.price.display : r.price) 
            : 'Fiyat bilgisi yok';
        const productUrl = r.product_url || r.link || r.url || '';
        const productDescription = r.why_recommended || r.description || '';
        const matchScore = r.match_score || 0;
        const sourceSite = r.source_site || '';
        
        console.log(`💰 Product ${index}: title="${productTitle}", price="${productPrice}", url="${productUrl}"`);
        
        // URL düzeltme ve validation
        let url = productUrl;
        let linkClass = 'buy-link';
        
        // URL temizleme ve doğrulama
        if (url) {
            console.log(`🔍 Original URL: ${url}`);
            
            // URL encoding problemlerini düzelt
            try {
                url = decodeURIComponent(url);
                console.log(`🔧 Decoded URL: ${url}`);
            } catch (e) {
                console.warn(`⚠️ URL decode failed: ${e}`);
            }
            
            // HTTP/HTTPS kontrolü
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                if (url.startsWith('www.') || url.includes('.com') || url.includes('.tr')) {
                    url = 'https://' + url.replace(/^(https?:\/\/)/, '');
                    console.log(`🔗 Added HTTPS: ${url}`);
                } else {
                    // Geçersiz URL ise Google aramasına yönlendir
                    const searchQuery = encodeURIComponent(productTitle);
                    url = `https://www.google.com/search?q=${searchQuery}+satın+al`;
                    console.log(`🔍 Fallback to Google: ${url}`);
                }
            }
            
            // URL'nin geçerli olduğundan emin ol
            try {
                new URL(url);
                console.log(`✅ Valid URL: ${url}`);
            } catch (e) {
                console.warn(`⚠️ Invalid URL detected: ${url}`);
                
                // Site-specific fallback URLs with enhanced product targeting
                let siteFound = false;
                const searchQuery = encodeURIComponent(productTitle);
                
                // Extract brand and model from product title for better targeting
                const foundBrand = extractBrand(productTitle);
                const foundModel = extractModel(productTitle);
                
                // Build enhanced search query
                let enhancedQuery = searchQuery;
                if (foundBrand) {
                    enhancedQuery = foundBrand + ' ' + searchQuery;
                }
                if (foundModel && !searchQuery.toLowerCase().includes(foundModel)) {
                    enhancedQuery += ' ' + foundModel;
                }
                
                console.log(`🎯 Enhanced search: "${productTitle}" → brand: "${foundBrand}", model: "${foundModel}", query: "${enhancedQuery}"`);
                
                // Category mapping for better site navigation
                const categoryMapping = {
                    'Headphones': 'kulaklik',
                    'Phone': 'cep-telefonu', 
                    'Laptop': 'laptop',
                    'Television': 'televizyon',
                    'Drone': 'drone',
                    'Klima': 'klima',
                    'Tire': 'lastik'
                };
                
                if (sourceSite) {
                    console.log(`🎯 Creating enhanced search URL for: ${sourceSite}`);
                    
                    const currentCat = getCurrentCategory();
                    const categoryPath = categoryMapping[currentCat] || '';
                    
                    // Fiyat bilgisini de URL'ye ekle
                    const price = r.price && typeof r.price === 'object' ? r.price.value : null;
                    const priceParam = price ? `&minPrice=${Math.max(0, price-1000)}&maxPrice=${price+1000}` : '';
                    
                    if (sourceSite.includes('teknosa')) {
                        // Teknosa enhanced URL with category and brand
                        url = `https://www.teknosa.com/arama?q=${enhancedQuery}${categoryPath ? '&kategori=' + categoryPath : ''}`;
                        console.log(`🔍 Teknosa enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('hepsiburada')) {
                        // Hepsiburada enhanced URL with specific product targeting
                        url = `https://www.hepsiburada.com/ara?q=${enhancedQuery}${priceParam}`;
                        console.log(`🔍 Hepsiburada enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('trendyol')) {
                        // Trendyol enhanced URL with brand and model focus
                        url = `https://www.trendyol.com/sr?q=${enhancedQuery}${foundBrand ? '&marka=' + foundBrand : ''}`;
                        console.log(`🔍 Trendyol enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('n11')) {
                        // N11 enhanced URL with precise product search
                        url = `https://www.n11.com/arama?q=${enhancedQuery}${foundBrand ? '&marka=' + foundBrand : ''}`;
                        console.log(`🔍 N11 enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('amazon')) {
                        // Amazon enhanced URL with department targeting
                        const dept = categoryPath ? `&i=${categoryPath}` : '';
                        url = `https://www.amazon.com.tr/s?k=${enhancedQuery}${dept}`;
                        console.log(`🔍 Amazon enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('gittigidiyor')) {
                        // GittiGidiyor enhanced URL
                        url = `https://www.gittigidiyor.com/arama/?k=${enhancedQuery}${foundBrand ? '&marka=' + foundBrand : ''}`;
                        console.log(`🔍 GittiGidiyor enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('ciceksepeti')) {
                        // ÇiçekSepeti enhanced URL for tech products
                        url = `https://www.ciceksepeti.com/arama?q=${enhancedQuery}`;
                        console.log(`🔍 ÇiçekSepeti enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('mediamarkt')) {
                        // MediaMarkt enhanced URL
                        url = `https://www.mediamarkt.com.tr/tr/search.html?query=${enhancedQuery}`;
                        console.log(`🔍 MediaMarkt enhanced URL: ${url}`);
                        siteFound = true;
                    } else if (sourceSite.includes('vatan')) {
                        // Vatan Bilgisayar enhanced URL
                        url = `https://www.vatanbilgisayar.com/arama/?text=${enhancedQuery}`;
                        console.log(`🔍 Vatan enhanced URL: ${url}`);
                        siteFound = true;
                    }
                }
                
                // Eğer site-specific URL yoksa Google search
                if (!siteFound) {
                    url = `https://www.google.com/search?q=${searchQuery}+satın+al`;
                    console.log(`🔍 Google fallback URL: ${url}`);
                }
                
                linkClass += ' link-fallback';
            }
        }
        
        // Link oluştur - link status'u da göster
        let linkHtml = '';
        if (url && url !== '' && !url.includes('undefined')) {
            let linkClass = 'buy-link';
            let linkIcon = 'fas fa-external-link-alt';
            let linkText = currentLanguage === 'tr' ? 'Satın Al' : 'Buy Now';
            
            // Link durumuna göre stil ve metin ayarla
            if (r.link_status) {
                switch (r.link_status) {
                    case 'valid':
                        linkClass += ' link-valid';
                        linkIcon = 'fas fa-check-circle';
                        break;
                    case 'repaired':
                        linkClass += ' link-repaired';
                        linkIcon = 'fas fa-tools';
                        linkText = currentLanguage === 'tr' ? 'Onarılan Link' : 'Repaired Link';
                        break;
                    case 'fallback':
                        linkClass += ' link-fallback';
                        linkIcon = 'fas fa-search';
                        linkText = currentLanguage === 'tr' ? 'Arama Sayfası' : 'Search Page';
                        break;
                    case 'failed':
                        linkClass += ' link-failed';
                        linkIcon = 'fas fa-exclamation-triangle';
                        linkText = currentLanguage === 'tr' ? 'Link Sorunlu' : 'Link Issue';
                        break;
                }
                
                // Link status mesajını tooltip olarak ekle
                const tooltipText = r.link_message || 'Link durumu';
                linkHtml = `<a href="${url}" target="_blank" rel="noopener noreferrer" class="${linkClass}" title="${tooltipText}">
                    <i class="${linkIcon}"></i> ${linkText}
                </a>`;
            } else {
                linkHtml = `<a href="${url}" target="_blank" rel="noopener noreferrer" class="${linkClass}">
                    <i class="${linkIcon}"></i> ${linkText}
                </a>`;
            }
        } else {
            // Geçersiz URL için disabled buton
            linkHtml = `<span class="buy-link link-failed" title="Geçersiz link">
                <i class="fas fa-exclamation-triangle"></i> ${currentLanguage === 'tr' ? 'Link Mevcut Değil' : 'Link Unavailable'}
            </span>`;
        }
        
        // Badge'leri ekle
        let badges = '';
        
        // Match score badge
        if (matchScore >= 90) {
            const perfectText = currentLanguage === 'tr' ? '⭐ Mükemmel Eşleşme' : '⭐ Perfect Match';
            badges += `<div class="premium-badge">${perfectText}</div>`;
        } else if (matchScore >= 80) {
            const goodText = currentLanguage === 'tr' ? '✅ İyi Eşleşme' : '✅ Good Match';
            badges += `<div class="good-badge">${goodText}</div>`;
        }
        
        // Site badge - sadece gerçek siteler için
        if (sourceSite && !sourceSite.includes('mock')) {
            badges += `<div class="site-badge">${sourceSite}</div>`;
        }
        
        // Features listesi
        let featuresHtml = '';
        if (r.features && Array.isArray(r.features)) {
            const featuresText = r.features.slice(0, 3).join(', '); // İlk 3 özellik
            featuresHtml = `<div class="recommendation-features">${featuresText}</div>`;
        }
        
        // Pros listesi
        let prosHtml = '';
        if (r.pros && Array.isArray(r.pros)) {
            const prosText = r.pros.slice(0, 2).map(pro => `✓ ${pro}`).join(' '); // İlk 2 artı
            prosHtml = `<div class="recommendation-pros">${prosText}</div>`;
        }
        
        html += `
            <div class="recommendation-item">
                ${badges}
                <div class="recommendation-content">
                    <div class="recommendation-name">${productTitle}</div>
                    <div class="recommendation-price">${productPrice}</div>
                    ${featuresHtml}
                    ${prosHtml}
                    ${productDescription ? `<div class="recommendation-description">${productDescription}</div>` : ''}
                    ${matchScore > 0 ? `<div class="match-score">Uygunluk: %${matchScore}</div>` : ''}
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
    
    // Hide all screens
    hideAICreationScreen();
    hideErrorScreen();
    
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
        showAICreationScreen();
    }
    
    const timeoutId = setTimeout(() => {
        if (isRequestInProgress) {
            console.log("Zaman aşımı oluştu!");
            isRequestInProgress = false;
            hideAICreationScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            showErrorScreen();
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
        console.log("🔄 Sunucudan gelen yanıt:", data);
        console.log("🔍 Response type:", data.type);
        console.log("🔍 Response keys:", Object.keys(data));
        console.log("🔍 Has recommendations:", !!data.recommendations);
        console.log("🔍 Has question:", !!data.question);
        console.log("🔍 Has options:", !!data.options);
        
        console.log("Response has question:", !!data.question);
        console.log("Response has options:", !!data.options);
        console.log("Response has recommendations:", !!data.recommendations);
        console.log("Response has error:", !!data.error);
        console.log("Response type:", data.type);
        console.log("Response keys:", Object.keys(data));
        
        if (data.question && data.options) {
            console.log("✅ Rendering question...");
            hideAICreationScreen();
            window.currentQuestionTooltip = data.tooltip || null;
            renderQuestion(data.question, data.options, data.emoji || '🔍');
        } else if (data.type === 'modern_recommendation' && data.recommendations) {
            console.log("✅ Modern recommendation path triggered");
            // Modern search engine response
            console.log("🚀 Modern recommendations found:", data.recommendations.length);
            console.log("📦 Modern recommendation data:", JSON.stringify(data, null, 2));
            
            hideAICreationScreen();
            renderRecommendations(data.recommendations);
            
            // Grounding results varsa göster
            if (data.grounding_results) {
                console.log("🔍 Grounding results:", data.grounding_results);
            }
            
            // Shopping results varsa göster
            if (data.shopping_results) {
                console.log("🛒 Shopping results:", data.shopping_results.length);
            }
            
            // Sources varsa göster
            if (data.sources) {
                console.log("📄 Sources:", data.sources.length);
            }
            
            // Modern search başarı bilgisi göster
            const modernMessage = currentLanguage === 'tr' ? 
                '✅ Online arama sistemi aktif - Güncel piyasa verilerimizle ürün önerilerinizi sunuyoruz.' : 
                '✅ Online search system active - Showing product recommendations with current market data.';
            
            showInfoMessage(modernMessage);
        } else if (data.type === 'fallback_recommendation' && data.recommendations) {
            console.log("✅ Fallback recommendation path triggered");
            // Fallback recommendations - güvenilir öneriler
            console.log("Fallback recommendations found:", data.recommendations.length);
            hideAICreationScreen();
            renderRecommendations(data.recommendations);
            
            // Fallback durumu için özel bildirim
            const fallbackMessage = currentLanguage === 'tr' ? 
                '⚠️ Online arama servisi şu anda kullanılamıyor. Size önceden hazırlanmış kaliteli ürün önerilerimizi sunuyoruz.' : 
                '⚠️ Online search service is currently unavailable. We are showing you our pre-prepared quality product recommendations.';
            
            showInfoMessage(fallbackMessage);
            
            // Ek mesaj varsa da göster
            if (data.message && data.message !== fallbackMessage) {
                setTimeout(() => showInfoMessage(data.message), 2000);
            }
        } else if (data.recommendations) {
            console.log("✅ Legacy recommendation path triggered");
            // Legacy recommendations
            renderRecommendations(data.recommendations);
        } else if (data.categories) {
            console.log("✅ Categories path triggered");
            renderLanding(data.categories);
        } else if (data.error) {
            console.log("❌ Error path triggered");
            hideAICreationScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            showErrorScreen();
        } else if (data.type === 'error' && data.fallback_recommendations) {
            console.log("✅ Error with fallback path triggered");
            // Error with fallback recommendations
            console.log("Error occurred but fallback recommendations provided");
            hideAICreationScreen();
            renderRecommendations(data.fallback_recommendations);
            
            // Error message'ı göster ama bloke etme
            const errorMsg = currentLanguage === 'tr' ? 
                'Arama sisteminde bir sorun oluştu, yedek öneriler gösteriliyor.' : 
                'Search system error occurred, showing fallback recommendations.';
            showInfoMessage(errorMsg);
        } else {
            console.error('❌ Hiçbir path eşleşmedi! Beklenmeyen yanıt formatı:', data);
            hideAICreationScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            showErrorScreen();
        }
    })
    .catch(err => {
        clearTimeout(timeoutId);
        isRequestInProgress = false;
        
        hideAICreationScreen();
        if (loadingElement) loadingElement.style.display = 'none';
        showErrorScreen();
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
    
    // Ürün arama ve filtreleme
    const productSearchInput = document.getElementById('product-search-input');
    const colorFilter = document.getElementById('color-filter');
    const sizeFilter = document.getElementById('size-filter');
    const ratingFilter = document.getElementById('rating-filter');
    const productSuggestions = document.getElementById('product-suggestions');
    const productList = document.getElementById('product-list');
    
    // Ürünleri yükle
    function loadProducts() {
        fetch('/products')
            .then(res => res.json())
            .then(data => {
                window.allProducts = data;
                renderProductList(data);
            })
            .catch(error => {
                console.error("Ürünler yüklenirken hata:", error);
            });
    }
    
    // Ürün listesini renderla
    function renderProductList(products) {
        productList.innerHTML = '';
        
        products.forEach(product => {
            const productItem = document.createElement('div');
            productItem.className = 'product-item';
            productItem.innerHTML = `
                <div class="product-image">
                    <img src="${product.image}" alt="${product.name}">
                </div>
                <div class="product-info">
                    <div class="product-name">${product.name}</div>
                    <div class="product-price">${product.price} ₺</div>
                </div>
            `;
            
            productItem.addEventListener('click', () => {
                // Ürün tıklandığında yapılacaklar
                console.log("Ürün tıklandı:", product);
            });
            
            productList.appendChild(productItem);
        });
    }
    
    // Arama ve filtreleme işlemini gerçekleştir
    function performSearchAndFilter() {
        const query = productSearchInput.value.toLowerCase().trim();
        const selectedColor = colorFilter.value;
        const selectedSize = sizeFilter.value;
        const selectedRating = ratingFilter.value;
        
        let filteredProducts = window.allProducts || [];
        
        // Ürün adında arama
        if (query) {
            filteredProducts = filteredProducts.filter(product => product.name.toLowerCase().includes(query));
        }
        
        // Renk filtresi
        if (selectedColor) {
            filteredProducts = filteredProducts.filter(product => product.color === selectedColor);
        }
        
        // Beden filtresi
        if (selectedSize) {
            filteredProducts = filteredProducts.filter(product => product.size === selectedSize);
        }
        
        // Puan filtresi
        if (selectedRating) {
            filteredProducts = filteredProducts.filter(product => product.rating >= parseInt(selectedRating));
        }
        
        renderProductList(filteredProducts);
    }
    
    // Olay dinleyicileri ekle
    productSearchInput.addEventListener('input', performSearchAndFilter);
    colorFilter.addEventListener('change', performSearchAndFilter);
    sizeFilter.addEventListener('change', performSearchAndFilter);
    ratingFilter.addEventListener('change', performSearchAndFilter);
    
    // Ürünleri yükle
    loadProducts();
};

// Ana sayfaya dönüş fonksiyonu
function goToHomePage() {
    // Tüm ekranları gizle
    hideErrorScreen();
    hideAICreationScreen();
    hideLoadingScreen();
    
    // Interaction'ı gizle ve landing'i göster
    document.getElementById('interaction').style.display = 'none';
    document.querySelector('.landing').style.display = 'block';
    
    // Değişkenleri sıfırla
    step = 0;
    category = null;
    answers = [];
    
    // Input'u temizle
    document.getElementById('chatbox-input').value = '';
    
    // Arama butonunu aktif hale getir
    const searchBtn = document.getElementById('chatbox-send');
    const originalText = currentLanguage === 'tr' ? '<i class="fas fa-search"></i> <span>AI ile Bul</span>' : '<i class="fas fa-search"></i> <span>Find with AI</span>';
    searchBtn.innerHTML = originalText;
    searchBtn.disabled = false;
}

// AI Creation Screen fonksiyonları
function showAICreationScreen() {
    document.getElementById('ai-creation-screen').style.display = 'flex';
    
    // Progress bar animasyonu
    setTimeout(() => {
        const progressBar = document.querySelector('.ai-progress-bar');
        if (progressBar) progressBar.style.width = '75%';
    }, 1000);
    
    setTimeout(() => {
        const progressBar = document.querySelector('.ai-progress-bar');
        if (progressBar) progressBar.style.width = '100%';
    }, 2000);
}

function hideAICreationScreen() {
    document.getElementById('ai-creation-screen').style.display = 'none';
    // Progress bar'ı sıfırla
    const progressBar = document.querySelector('.ai-progress-bar');
    if (progressBar) progressBar.style.width = '45%';
}

// Error Screen fonksiyonları
function showInfoMessage(message) {
    // Info mesajı için stil oluştur
    const infoDiv = document.createElement('div');
    infoDiv.className = 'info-message';
    infoDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.3);
        z-index: 10000;
        max-width: 350px;
        font-size: 14px;
        line-height: 1.4;
        animation: slideInRight 0.3s ease;
    `;
    infoDiv.innerHTML = `
        <i class="fas fa-info-circle" style="margin-right: 8px; color: #fbbf24;"></i>
        ${message}
    `;
    
    document.body.appendChild(infoDiv);
    
    // 5 saniye sonra otomatik olarak kaldır
    setTimeout(() => {
        if (infoDiv.parentNode) {
            infoDiv.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(infoDiv);
            }, 300);
        }
    }, 5000);
    
    // Tıklayınca kapat
    infoDiv.addEventListener('click', () => {
        if (infoDiv.parentNode) {
            infoDiv.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(infoDiv);
            }, 300);
        }
    });
}

function showErrorScreen() {
    document.getElementById('error-screen').style.display = 'flex';
}

function hideErrorScreen() {
    document.getElementById('error-screen').style.display = 'none';
}

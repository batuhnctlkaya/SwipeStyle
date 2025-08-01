/**
 * SwipeStyle Frontend JavaScript
 * Basit ve temiz JavaScript kodu
 */

// Global dil değişkeni
let currentLanguage = 'tr';
let currentTheme = 'light';

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
            step = 1;
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
            
            console.log("SwipeStyle başarıyla başlatıldı");
        })
        .catch(error => {
            console.error("Kategoriler yüklenirken hata oluştu:", error);
            const errorMsg = currentLanguage === 'tr' ? "Kategoriler yüklenemedi. Lütfen sayfayı yenileyin." : "Categories could not be loaded. Please refresh the page.";
            document.querySelector('.error').textContent = errorMsg;
        });
};

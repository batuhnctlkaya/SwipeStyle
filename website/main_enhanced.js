/**
 * SwipeStyle Gelişmiş Frontend JavaScript
 * =======================================
 * 
 * Bu dosya, SwipeStyle uygulamasının frontend fonksiyonalitesini sağlar.
 * Çoklu dil desteği, ülke seçimi ve Google Shopping entegrasyonu içerir.
 * 
 * Ana Özellikler:
 * - Dil/ülke ayarları yönetimi
 * - Session tracking
 * - Kategori yükleme ve görüntüleme
 * - Arama fonksiyonalitesi
 * - Soru-cevap akışı
 * - Shopping önerileri
 * - Responsive tasarım
 * 
 * API Endpoint'leri:
 * - /settings (GET/POST): Kullanıcı ayarları
 * - /detect_category: Kategori tespiti
 * - /categories: Kategori listesi
 * - /ask: Soru-cevap akışı
 * - /shopping: Ürün önerileri
 * 
 * Kullanım:
 * Bu dosya main_enhanced.html ile birlikte çalışır.
 * Sayfa yüklendiğinde otomatik olarak başlatılır.
 */

class SwipeStyleApp {
    constructor() {
        // Uygulama durumu
        this.currentLanguage = 'tr';
        this.currentCountry = 'TR';
        this.sessionId = null;
        this.currentCategory = null;
        this.currentStep = 0;
        this.answers = [];
        
        // DOM elementleri
        this.elements = {};
        
        // Çeviri sözlüğü
        this.translations = {
            tr: {
                subtitle: 'Akıllı Ürün Tavsiye Sistemi',
                searchTitle: 'Ne arıyorsunuz?',
                searchPlaceholder: 'Örn: kablosuz kulaklık, gaming laptop...',
                findButton: '🔍 Ara',
                categoriesTitle: 'Kategoriler',
                loadingText: 'Yükleniyor...',
                productsTitle: 'Önerilen Ürünler',
                saveSettings: '💾 Ayarları Kaydet',
                settingsSaved: 'Ayarlar başarıyla kaydedildi!',
                errorOccurred: 'Bir hata oluştu. Lütfen tekrar deneyin.',
                categoryCreated: 'Yeni kategori oluşturuldu',
                noProducts: 'Ürün bulunamadı.',
                viewProduct: 'Ürünü Gör'
            },
            en: {
                subtitle: 'Smart Product Recommendation System',
                searchTitle: 'What are you looking for?',
                searchPlaceholder: 'e.g: wireless headphones, gaming laptop...',
                findButton: '🔍 Find',
                categoriesTitle: 'Categories',
                loadingText: 'Loading...',
                productsTitle: 'Recommended Products',
                saveSettings: '💾 Save Settings',
                settingsSaved: 'Settings saved successfully!',
                errorOccurred: 'An error occurred. Please try again.',
                categoryCreated: 'New category created',
                noProducts: 'No products found.',
                viewProduct: 'View Product'
            }
        };
        
        this.init();
    }
    
    /**
     * Uygulamayı başlatır
     */
    async init() {
        this.bindElements();
        this.bindEvents();
        await this.loadUserSettings();
        this.updateUI();
        await this.loadCategories();
    }
    
    /**
     * DOM elementlerini bağlar
     */
    bindElements() {
        this.elements = {
            languageSelect: document.getElementById('languageSelect'),
            countrySelect: document.getElementById('countrySelect'),
            saveSettings: document.getElementById('saveSettings'),
            subtitle: document.getElementById('subtitle'),
            searchTitle: document.getElementById('searchTitle'),
            searchInput: document.getElementById('searchInput'),
            searchButton: document.getElementById('searchButton'),
            categoriesTitle: document.getElementById('categoriesTitle'),
            categoryGrid: document.getElementById('categoryGrid'),
            loadingDiv: document.getElementById('loadingDiv'),
            loadingText: document.getElementById('loadingText'),
            messageArea: document.getElementById('messageArea'),
            questionSection: document.getElementById('questionSection'),
            questionText: document.getElementById('questionText'),
            optionsDiv: document.getElementById('optionsDiv'),
            shoppingResults: document.getElementById('shoppingResults'),
            productsTitle: document.getElementById('productsTitle'),
            productsGrid: document.getElementById('productsGrid')
        };
    }
    
    /**
     * Event listener'ları bağlar
     */
    bindEvents() {
        // Ayarlar
        this.elements.saveSettings.addEventListener('click', () => this.saveUserSettings());
        this.elements.languageSelect.addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            this.updateUI();
        });
        this.elements.countrySelect.addEventListener('change', (e) => {
            this.currentCountry = e.target.value;
        });
        
        // Arama
        this.elements.searchButton.addEventListener('click', () => this.handleSearch());
        this.elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
    }
    
    /**
     * Kullanıcı ayarlarını yükler
     */
    async loadUserSettings() {
        try {
            const response = await fetch('/api/user-settings');
            const data = await response.json();
            
            if (data.settings) {
                this.currentLanguage = data.settings.language || 'tr';
                this.currentCountry = data.settings.country || 'TR';
                this.sessionId = data.settings.session_id;
                
                // Select elementlerini güncelle
                this.elements.languageSelect.value = this.currentLanguage;
                this.elements.countrySelect.value = this.currentCountry;
            }
        } catch (error) {
            console.error('Settings yüklenemedi:', error);
        }
    }
    
    /**
     * Kullanıcı ayarlarını kaydeder
     */
    async saveUserSettings() {
        try {
            const response = await fetch('/api/user-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    language: this.currentLanguage,
                    country: this.currentCountry,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.sessionId = data.session_id;
                this.showMessage(this.t('settingsSaved'), 'success');
                await this.loadCategories(); // Kategorileri yeniden yükle
            } else {
                this.showMessage(data.error || this.t('errorOccurred'), 'error');
            }
        } catch (error) {
            console.error('Settings kaydedilemedi:', error);
            this.showMessage(this.t('errorOccurred'), 'error');
        }
    }
    
    /**
     * UI'ı mevcut dile göre günceller
     */
    updateUI() {
        this.elements.subtitle.textContent = this.t('subtitle');
        this.elements.searchTitle.textContent = this.t('searchTitle');
        this.elements.searchInput.placeholder = this.t('searchPlaceholder');
        this.elements.searchButton.innerHTML = this.t('findButton');
        this.elements.categoriesTitle.textContent = this.t('categoriesTitle');
        this.elements.loadingText.textContent = this.t('loadingText');
        this.elements.productsTitle.textContent = this.t('productsTitle');
        this.elements.saveSettings.innerHTML = this.t('saveSettings');
    }
    
    /**
     * Çeviri helper fonksiyonu
     */
    t(key) {
        return this.translations[this.currentLanguage][key] || key;
    }
    
    /**
     * Kategorileri yükler ve görüntüler
     */
    async loadCategories() {
        try {
            const url = `/api/categories?language=${this.currentLanguage}&session_id=${this.sessionId || ''}`;
            const response = await fetch(url);
            const data = await response.json();
            
            this.displayCategories(data.categories || {});
        } catch (error) {
            console.error('Kategoriler yüklenemedi:', error);
            this.showMessage(this.t('errorOccurred'), 'error');
        }
    }
    
    /**
     * Kategorileri görüntüler
     */
    displayCategories(categories) {
        this.elements.categoryGrid.innerHTML = '';
        
        // Categories artık array formatında geliyor
        if (Array.isArray(categories)) {
            categories.forEach(category => {
                const card = document.createElement('div');
                card.className = 'category-card';
                card.onclick = () => this.selectCategory(category.name);
                
                const emoji = category.emoji || '📱';
                
                card.innerHTML = `
                    <span class="category-emoji">${emoji}</span>
                    <div class="category-name">${category.name}</div>
                `;
                
                this.elements.categoryGrid.appendChild(card);
            });
        } else {
            // Eski format için backward compatibility
            Object.entries(categories).forEach(([categoryName, categoryData]) => {
                const card = document.createElement('div');
                card.className = 'category-card';
                card.onclick = () => this.selectCategory(categoryName);
                
                // İlk spec'ten emoji al
                const emoji = categoryData.specs && categoryData.specs[0] ? 
                    categoryData.specs[0].emoji : '📱';
                
                card.innerHTML = `
                    <span class="category-emoji">${emoji}</span>
                    <div class="category-name">${categoryName}</div>
                `;
                
                this.elements.categoryGrid.appendChild(card);
            });
        }
    }
    
    /**
     * Arama işlemini gerçekleştirir
     */
    async handleSearch() {
        const query = this.elements.searchInput.value.trim();
        if (!query) return;
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/create-category', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    category_name: query,
                    language: this.currentLanguage,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success && data.category) {
                this.sessionId = data.session_id;
                this.selectCategory(data.category.name);
                if (data.created) {
                    this.showMessage(`✅ ${this.t('categoryCreated')}: ${data.category.name}`, 'success');
                }
            } else {
                const errorMsg = data.error || this.t('errorOccurred');
                if (errorMsg.includes('429') || errorMsg.includes('quota')) {
                    this.showMessage('⚠️ AI servisi geçici olarak yoğun. Lütfen birkaç saniye bekleyin ve tekrar deneyin.', 'error');
                } else {
                    this.showMessage(`❌ ${errorMsg}`, 'error');
                }
            }
        } catch (error) {
            console.error('Arama hatası:', error);
            this.showMessage(this.t('errorOccurred'), 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    /**
     * Kategori seçimi
     */
    async selectCategory(categoryName) {
        this.currentCategory = categoryName;
        this.currentStep = 0;  // 0-based indexing for questions
        this.answers = [];
        
        // Ana içeriği gizle ve soru bölümünü göstermek için hazırla
        this.hideMainContent();
        
        await this.askNextQuestion();
    }
    
    /**
     * Sonraki soruyu sorar
     */
    async askNextQuestion() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    step: this.currentStep,
                    category: this.currentCategory,
                    answers: this.answers,
                    language: this.currentLanguage,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.question) {
                this.displayQuestion(data);
            } else if (data.recommendations) {
                console.log('Recommendations received:', data.recommendations);
                await this.showRecommendations(data.recommendations);
            } else {
                console.log('No question or recommendations found in response:', data);
                this.showMessage(data.error || this.t('errorOccurred'), 'error');
            }
        } catch (error) {
            console.error('Soru sorma hatası:', error);
            this.showMessage(this.t('errorOccurred'), 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    /**
     * Soruyu görüntüler
     */
    displayQuestion(data) {
        const emoji = data.emoji || '❓';
        this.elements.questionText.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <button class="back-button" onclick="window.swipeStyleApp.goBackToCategories()">← Kategorilere Dön</button>
                <span style="font-size: 0.9em; color: #666;">${this.currentCategory}</span>
            </div>
            <span class="question-emoji">${emoji}</span>
            ${data.question}
        `;
        
        this.elements.optionsDiv.innerHTML = '';
        
        data.options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-button';
            button.textContent = option;
            button.onclick = () => this.answerQuestion(option);
            this.elements.optionsDiv.appendChild(button);
        });
        
        this.elements.questionSection.style.display = 'block';
    }
    
    /**
     * Kategorilere geri dön
     */
    goBackToCategories() {
        this.currentCategory = null;
        this.currentStep = 0;
        this.answers = [];
        this.hideElements();
        this.showMainContent();
    }
    
    /**
     * Soruyu cevaplar
     */
    async answerQuestion(answer) {
        this.answers.push(answer);
        this.currentStep++;
        
        this.elements.questionSection.style.display = 'none';
        await this.askNextQuestion();
    }
    
    /**
     * Önerileri gösterir ve shopping sonuçlarını yükler
     */
    async showRecommendations(recommendations) {
        console.log('showRecommendations called with:', recommendations);
        
        // Önce AI önerilerini göster (varsa)
        if (recommendations && recommendations.length > 0) {
            console.log('Displaying AI recommendations:', recommendations.length, 'items');
            this.displayAIRecommendations(recommendations);
        } else {
            console.log('No AI recommendations, loading shopping results instead');
            // AI önerileri yoksa Google Shopping sonuçlarını yükle
            await this.loadShoppingResults();
        }
    }
    
    /**
     * AI önerilerini görüntüler
     */
    displayAIRecommendations(recommendations) {
        // Soru bölümünü gizle
        this.elements.questionSection.style.display = 'none';
        
        this.elements.productsGrid.innerHTML = '';
        
        // AI önerileri başlığını güncelle
        this.elements.productsTitle.textContent = this.currentLanguage === 'tr' ? 
            '🤖 AI Önerileri' : '🤖 AI Recommendations';
        
        recommendations.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card ai-recommendation';
            
            const rating = product.rating ? 
                `<div class="product-rating">⭐ ${product.rating}</div>` : '';
            
            const description = product.description ? 
                `<div class="product-description">${product.description}</div>` : '';
            
            card.innerHTML = `
                ${product.image && product.image !== 'placeholder.jpg' ? 
                    `<img src="${product.image}" alt="${product.name}" class="product-image" onerror="this.style.display='none'">` : 
                    `<div class="product-image ai-placeholder" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px;">🤖</div>`
                }
                <div class="product-info">
                    <div class="product-title ai-title">${product.name}</div>
                    <div class="product-price ai-price">${product.price}</div>
                    ${description}
                    ${rating}
                    ${product.link ? 
                        `<a href="${product.link}" target="_blank" class="product-link ai-link">${this.t('viewProduct')}</a>` : 
                        ''
                    }
                </div>
            `;
            
            this.elements.productsGrid.appendChild(card);
        });
        
        // Sonuçları göster
        this.elements.shoppingResults.style.display = 'block';
        
        // AI öneriler için özel stil ekle
        if (!document.getElementById('ai-recommendations-style')) {
            const style = document.createElement('style');
            style.id = 'ai-recommendations-style';
            style.textContent = `
                .ai-recommendation {
                    border: 2px solid #667eea !important;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
                }
                .ai-title {
                    color: #667eea !important;
                    font-weight: 600 !important;
                }
                .ai-price {
                    color: #764ba2 !important;
                    font-weight: bold !important;
                }
                .ai-link {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    color: white !important;
                }
                .ai-placeholder {
                    height: 200px !important;
                }
                .product-description {
                    font-size: 14px;
                    color: #666;
                    margin: 8px 0;
                    line-height: 1.4;
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Google Shopping sonuçlarını yükler
     */
    async loadShoppingResults() {
        try {
            const query = this.elements.searchInput.value || this.currentCategory;
            
            const response = await fetch('/api/shopping', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    country: this.currentCountry,
                    language: this.currentLanguage,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.products && data.products.length > 0) {
                this.displayProducts(data.products);
            } else {
                this.showMessage(this.t('noProducts'), 'error');
            }
        } catch (error) {
            console.error('Shopping sonuçları yüklenemedi:', error);
            this.showMessage(this.t('errorOccurred'), 'error');
        }
    }
    
    /**
     * Ürünleri görüntüler
     */
    displayProducts(products) {
        this.elements.productsGrid.innerHTML = '';
        
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            
            const rating = product.rating ? 
                `<div class="product-rating">⭐ ${product.rating} (${product.reviews || 0})</div>` : '';
            
            card.innerHTML = `
                ${product.image ? 
                    `<img src="${product.image}" alt="${product.title}" class="product-image" onerror="this.style.display='none'">` : 
                    `<div class="product-image" style="background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;">📷 No Image</div>`
                }
                <div class="product-info">
                    <div class="product-title">${product.title}</div>
                    <div class="product-price">${product.price}</div>
                    <div class="product-source">${product.source}</div>
                    ${rating}
                    ${product.link ? 
                        `<a href="${product.link}" target="_blank" class="product-link">${this.t('viewProduct')}</a>` : 
                        ''
                    }
                </div>
            `;
            
            this.elements.productsGrid.appendChild(card);
        });
        
        this.elements.shoppingResults.style.display = 'block';
    }
    
    /**
     * Loading durumunu gösterir/gizler
     */
    showLoading(show) {
        this.elements.loadingDiv.style.display = show ? 'block' : 'none';
    }
    
    /**
     * Mesaj gösterir
     */
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        this.elements.messageArea.innerHTML = '';
        this.elements.messageArea.appendChild(messageDiv);
        
        // 5 saniye sonra mesajı kaldır
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
    
    /**
     * Ana içeriği gizler (kategoriler, arama vs)
     */
    hideMainContent() {
        // Ana içerik bölümlerini gizle
        if (document.querySelector('.search-section')) {
            document.querySelector('.search-section').style.display = 'none';
        }
        if (document.querySelector('.categories-section')) {
            document.querySelector('.categories-section').style.display = 'none';
        }
        // Diğer elementleri de gizle
        this.hideElements();
    }
    
    /**
     * Ana içeriği gösterir
     */
    showMainContent() {
        // Ana içerik bölümlerini göster
        if (document.querySelector('.search-section')) {
            document.querySelector('.search-section').style.display = 'block';
        }
        if (document.querySelector('.categories-section')) {
            document.querySelector('.categories-section').style.display = 'block';
        }
    }

    /**
     * Elementleri gizler
     */
    hideElements() {
        this.elements.questionSection.style.display = 'none';
        this.elements.shoppingResults.style.display = 'none';
        this.elements.messageArea.innerHTML = '';
    }
}

// Sayfa yüklendiğinde uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    window.swipeStyleApp = new SwipeStyleApp();
});

// Global fonksiyonlar (debug için)
window.resetApp = () => {
    if (window.swipeStyleApp) {
        window.swipeStyleApp.goBackToCategories();
    }
};

console.log('SwipeStyle Enhanced JS loaded! 🚀');

/**
 * SwipeStyle Frontend JavaScript Modülü
 * =====================================
 * 
 * Bu dosya, SwipeStyle uygulamasının frontend JavaScript kodlarını içerir.
 * Kullanıcı arayüzü etkileşimlerini yönetir, API çağrıları yapar ve
 * dinamik içerik güncellemeleri sağlar.
 * 
 * Ana Özellikler:
 * - Kategori kartları render etme
 * - Soru-cevap akışı yönetimi
 * - Loading ekranları
 * - Ürün önerileri gösterimi
 * - Hata yönetimi
 * 
 * API Endpoint'leri:
 * - /detect_category: Kategori tespiti
 * - /categories: Kategori listesi
 * - /ask: Soru-cevap akışı
 * 
 * Kullanım:
 * HTML dosyasında defer ile yüklenir
 * Sayfa yüklendiğinde otomatik olarak başlatılır
 */

// Chatbox logic
/**
 * Kullanıcının arama kutusuna yazdığı sorguyu işler.
 * 
 * Bu fonksiyon, kullanıcının arama kutusuna yazdığı metni alır
 * ve backend'e göndererek kategori tespiti yapar. Eğer kategori
 * bulunursa, soru-cevap akışını başlatır.
 * 
 * İşlem Adımları:
 * 1. Arama kutusundan metni alır
 * 2. Loading ekranını gösterir
 * 3. /detect_category endpoint'ine POST isteği gönderir
 * 4. Yanıtı işler ve akışı başlatır
 * 
 * Hata Durumları:
 * - Boş sorgu: İşlem yapılmaz
 * - API hatası: Kullanıcıya hata mesajı gösterilir
 * - Kategori bulunamadı: Uyarı mesajı gösterilir
 */
function handleChatboxEntry() {
    const input = document.getElementById('chatbox-input').value.trim();
    if (!input) return;
    showLoadingScreen();
    fetch('/detect_category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
    })
    .then(async res => {
        let data = await res.json();
        hideLoadingScreen();
        if (res.ok && data.category) {
            category = data.category;
            step = 1;
            answers = [];
            document.querySelector('.landing').style.display = 'none';
            document.getElementById('interaction').style.display = '';
            askAgent();
        } else if (data.error) {
            showNotification(data.error, 'error');
        } else {
            showNotification('Kategori tespit edilemedi. Lütfen daha açık bir istek girin.', 'warning');
        }
    })
    .catch(() => {
        hideLoadingScreen();
        showNotification('Sunucuya erişilemiyor. Lütfen daha sonra tekrar deneyin.', 'error');
    });
}

/**
 * Sayfa yüklendiğinde çalışan ana fonksiyon.
 * 
 * Bu fonksiyon, sayfa tamamen yüklendiğinde çalışır ve:
 * 1. Kategorileri backend'den yükler
 * 2. Kategori kartlarını render eder
 * 3. Event listener'ları ayarlar
 * 
 * Yapılan İşlemler:
 * - /categories endpoint'inden kategori listesi alınır
 * - Her kategori için özellikler (specs) kaydedilir
 * - Kategori kartları oluşturulur
 * - Arama kutusu event listener'ları eklenir
 */
window.onload = () => {
    // Get categories and specs from backend
    fetch('/categories')
        .then(res => res.json())
        .then(data => {
            const categories = Object.keys(data);
            window.currentSpecs = {};
            for (const cat of categories) {
                window.currentSpecs[cat] = data[cat].specs || [];
            }
            renderLanding(categories);
        });
    // Chatbox event
    document.getElementById('chatbox-send').onclick = handleChatboxEntry;
    document.getElementById('chatbox-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') handleChatboxEntry();
    });
};

// Global değişkenler
let step = 0;        // Mevcut adım (0: kategori seçimi, 1-N: sorular)
let category = null; // Seçilen kategori
let answers = [];    // Verilen cevaplar listesi

/**
 * Kategori ikonları sözlüğü - Sade ve şık ikonlar.
 * 
 * Her kategori için modern emoji ikonu tanımlar.
 * Eğer kategori bu listede yoksa, varsayılan olarak 🔍 kullanılır.
 */
const categoryIcons = {
    'Mouse': '🖱️',
    'Headphones': '🎧',
    'Phone': '📱',
    'Laptop': '💻'
};

/**
 * Kategori renkleri - Sade renk paleti.
 */
const categoryColors = {
    'Mouse': '#3182ce',
    'Headphones': '#805ad5',
    'Phone': '#38a169',
    'Laptop': '#dd6b20'
};

/**
 * Ana sayfa kategori kartlarını render eder.
 * 
 * Bu fonksiyon, backend'den gelen kategori listesini alır
 * ve her kategori için tıklanabilir kart oluşturur.
 * 
 * Args:
 *     categories (Array): Kategori adları listesi
 * 
 * Oluşturulan Kartlar:
 * - Her kart tıklanabilir
 * - Kategori ikonu ve adı gösterilir
 * - Hover efektleri vardır
 * - Tıklandığında startInteraction() çağrılır
 */
function renderLanding(categories) {
    const grid = document.getElementById('category-cards');
    grid.innerHTML = '';
    categories.forEach(cat => {
        const card = document.createElement('div');
        card.className = 'category-card';
        card.onclick = () => startInteraction(cat);
        
        const icon = document.createElement('div');
        icon.className = 'category-icon';
        icon.textContent = categoryIcons[cat] || '🔍';
        
        // Kategori rengini uygula
        if (categoryColors[cat]) {
            icon.style.color = categoryColors[cat];
        }
        
        const label = document.createElement('div');
        label.className = 'category-label';
        label.textContent = cat;
        
        card.appendChild(icon);
        card.appendChild(label);
        grid.appendChild(card);
    });
    // Attach chatbox event listeners after rendering
    const chatboxSend = document.getElementById('chatbox-send');
    const chatboxInput = document.getElementById('chatbox-input');
    if (chatboxSend && chatboxInput) {
        chatboxSend.onclick = handleChatboxEntry;
        chatboxInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleChatboxEntry();
        });
    }
}

/**
 * Kategori seçimi sonrası etkileşimi başlatır.
 * 
 * Bu fonksiyon, kullanıcı bir kategori seçtiğinde çağrılır.
 * Global değişkenleri günceller ve soru-cevap akışını başlatır.
 * 
 * Args:
 *     selectedCategory (string): Seçilen kategori adı
 * 
 * Yapılan İşlemler:
 * - Global category değişkeni güncellenir
 * - step 1'e ayarlanır
 * - answers listesi temizlenir
 * - Ana sayfa gizlenir, etkileşim alanı gösterilir
 * - askAgent() çağrılır
 */
function startInteraction(selectedCategory) {
    category = selectedCategory;
    step = 1;
    answers = [];
    document.querySelector('.landing').style.display = 'none';
    document.getElementById('interaction').style.display = '';
    askAgent();
}

/**
 * Soru kartını render eder - Sade ve şık tasarım.
 * 
 * Bu fonksiyon, backend'den gelen soru verilerini alır
 * ve kullanıcı dostu bir kart şeklinde gösterir.
 * 
 * Args:
 *     question (string): Soru metni
 *     options (Array): Seçenekler listesi (genellikle ["Yes", "No"])
 *     emoji (string): Soru ile ilgili emoji
 * 
 * Oluşturulan Kart:
 * - Temiz arka plan
 * - Emoji, soru metni ve seçenek butonları
 * - Responsive tasarım
 * - Hover efektleri
 */
function renderQuestion(question, options, emoji) {
    document.querySelector('.loading').style.display = 'none';
    const qDiv = document.querySelector('.question');
    qDiv.innerHTML = '';
    const card = document.createElement('div');
    card.style.background = '#ffffff';
    card.style.borderRadius = '16px';
    card.style.boxShadow = '0 4px 20px rgba(0,0,0,0.08)';
    card.style.width = '500px';
    card.style.margin = '40px auto';
    card.style.padding = '40px 30px';
    card.style.display = 'flex';
    card.style.flexDirection = 'column';
    card.style.alignItems = 'center';
    card.style.justifyContent = 'center';
    card.style.position = 'relative';
    card.style.border = '1px solid #e2e8f0';
    
    // Emoji
    const emojiDiv = document.createElement('div');
    emojiDiv.style.fontSize = '3.5em';
    emojiDiv.style.marginBottom = '20px';
    emojiDiv.style.color = '#3182ce';
    emojiDiv.textContent = emoji || '🔍';
    card.appendChild(emojiDiv);
    
    // Question
    const qText = document.createElement('div');
    qText.style.fontSize = '1.6em';
    qText.style.fontWeight = '500';
    qText.style.textAlign = 'center';
    qText.style.marginBottom = '30px';
    qText.style.lineHeight = '1.4';
    qText.style.color = '#2d3748';
    qText.textContent = question;
    card.appendChild(qText);
    
    // Options
    const optionsDiv = document.createElement('div');
    optionsDiv.style.display = 'flex';
    optionsDiv.style.gap = '20px';
    optionsDiv.style.flexWrap = 'wrap';
    optionsDiv.style.justifyContent = 'center';
    
    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.textContent = opt === 'Yes' ? 'Evet' : 'Hayır';
        btn.style.padding = '12px 32px';
        btn.style.fontSize = '1.1em';
        btn.style.borderRadius = '8px';
        btn.style.border = 'none';
        btn.style.cursor = 'pointer';
        btn.style.background = opt === 'Yes' ? '#3182ce' : '#718096';
        btn.style.color = '#ffffff';
        btn.style.fontWeight = '500';
        btn.style.transition = 'all 0.2s ease';
        btn.onclick = () => handleOption(opt);
        btn.onmouseenter = () => {
            btn.style.transform = 'translateY(-1px)';
            btn.style.background = opt === 'Yes' ? '#2c5aa0' : '#4a5568';
        };
        btn.onmouseleave = () => {
            btn.style.transform = 'translateY(0)';
            btn.style.background = opt === 'Yes' ? '#3182ce' : '#718096';
        };
        optionsDiv.appendChild(btn);
    });
    card.appendChild(optionsDiv);
    qDiv.appendChild(card);
    document.querySelector('.recommendation').innerHTML = '';
    document.querySelector('.error').textContent = '';
}

/**
 * Ürün önerilerini render eder - Sade ve şık tasarım.
 * 
 * Bu fonksiyon, backend'den gelen ürün önerilerini alır
 * ve kullanıcı dostu bir liste şeklinde gösterir.
 * 
 * Args:
 *     recs (Array): Ürün önerileri listesi
 *         Her öneri: {name: string, price: string, link: string}
 * 
 * Oluşturulan İçerik:
 * - Başlık: "Önerilen Ürünler"
 * - Her ürün için: ad, fiyat ve satın alma linki
 * - "Yeni arama yap" butonu
 * - Linkler yeni sekmede açılır
 */
function renderRecommendations(recs) {
    hideLoadingScreen();
    const recDiv = document.querySelector('.recommendation');
    
    let html = `
        <div style="text-align: center; margin-bottom: 40px;">
            <h2 style="font-size: 2.2em; color: #2d3748; margin-bottom: 16px; font-weight: 500;">
                Önerilen Ürünler
            </h2>
            <p style="color: #718096; font-size: 1.1em;">
                Size en uygun ürünleri bulduk
            </p>
        </div>
    `;
    
    recs.forEach((r, index) => {
        let linkHtml = '';
        let url = r.link || '';
        if (url && !url.startsWith('http') && url.length > 5) {
            url = 'https://' + url.replace(/^(www\.)?/, '');
        }
        if (url && url.startsWith('http')) {
            linkHtml = ` <a href="${url}" target="_blank" style="color:#ffffff; text-decoration:none; background:#3182ce; padding:8px 16px; border-radius:6px; font-weight:500; margin-left:12px;">Satın Al</a>`;
        }
        
        html += `
            <div style="
                background: #ffffff;
                margin-bottom: 16px;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                border: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 12px;
            ">
                <div style="flex: 1; min-width: 200px;">
                    <div style="font-size: 1.2em; font-weight: 500; color: #2d3748; margin-bottom: 6px;">
                        ${r.name}
                    </div>
                    <div style="font-size: 1em; color: #3182ce; font-weight: 500;">
                        ${r.price}
                    </div>
                </div>
                ${linkHtml}
            </div>
        `;
    });
    
    html += `
        <div style="text-align: center; margin-top: 32px;">
            <button id="back-to-categories" style="
                padding: 14px 32px;
                font-size: 1.1em;
                border-radius: 8px;
                border: none;
                background: #3182ce;
                color: #ffffff;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s ease;
            ">Yeni Arama Yap</button>
        </div>
    `;
    
    recDiv.innerHTML = html;
    document.querySelector('.error').textContent = '';
    
    // Back button hover effect
    const backBtn = document.getElementById('back-to-categories');
    if (backBtn) {
        backBtn.onmouseenter = () => {
            backBtn.style.transform = 'translateY(-1px)';
            backBtn.style.background = '#2c5aa0';
        };
        backBtn.onmouseleave = () => {
            backBtn.style.transform = 'translateY(0)';
            backBtn.style.background = '#3182ce';
        };
        backBtn.onclick = () => {
            document.getElementById('interaction').style.display = 'none';
            document.querySelector('.landing').style.display = '';
            document.querySelector('.recommendation').innerHTML = '';
            document.querySelector('.question').innerHTML = '';
            document.querySelector('.options').innerHTML = '';
            document.querySelector('.error').textContent = '';
            step = 0;
            category = null;
            answers = [];
        };
    }
}

/**
 * Bildirim gösterme fonksiyonu.
 */
function showNotification(message, type = 'info') {
    // Mevcut bildirimi kaldır
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: #ffffff;
        font-weight: 500;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease;
    `;
    
    const colors = {
        'error': '#e53e3e',
        'warning': '#dd6b20',
        'success': '#38a169',
        'info': '#3182ce'
    };
    
    notification.style.background = colors[type] || colors.info;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 5 saniye sonra kaldır
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
    
    // CSS animasyonları
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

/**
 * Tam ekran loading ekranını gösterir - Sade tasarım.
 * 
 * Bu fonksiyon, uzun süren işlemler sırasında kullanıcıya
 * görsel geri bildirim sağlar. Özellikle ürün önerileri
 * alınırken kullanılır.
 * 
 * Özellikler:
 * - Yarı şeffaf arka plan
 * - Dönen loading animasyonu
 * - Bilgilendirici mesaj
 * - Sayfanın üzerinde gösterilir (z-index: 9999)
 */
function showLoadingScreen() {
    hideLoadingScreen();
    const interaction = document.getElementById('interaction');
    let loadingDiv = document.getElementById('custom-loading');
    if (!loadingDiv) {
        loadingDiv = document.createElement('div');
        loadingDiv.id = 'custom-loading';
        loadingDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(248, 250, 252, 0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        loadingDiv.innerHTML = `
            <div style="margin-bottom: 24px;">
                <div style="
                    width: 60px;
                    height: 60px;
                    border: 4px solid #e2e8f0;
                    border-top: 4px solid #3182ce;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                "></div>
            </div>
            <div style="font-size: 1.3em; color: #2d3748; font-weight: 500; text-align: center;">
                Ürünler aranıyor...
            </div>
            <div style="font-size: 1em; color: #718096; margin-top: 8px; text-align: center;">
                Size en uygun ürünleri buluyoruz
            </div>
            <style>
            @keyframes spin { 
                0% { transform: rotate(0deg);} 
                100% { transform: rotate(360deg);} 
            }
            </style>
        `;
        document.body.appendChild(loadingDiv);
    }
    loadingDiv.style.display = 'flex';
}

/**
 * Loading ekranını gizler.
 * 
 * Bu fonksiyon, loading ekranını kaldırır ve
 * normal sayfa içeriğini gösterir.
 */
function hideLoadingScreen() {
    let loadingDiv = document.getElementById('custom-loading');
    if (loadingDiv) loadingDiv.style.display = 'none';
}

/**
 * Kullanıcı seçenek seçtiğinde çağrılır.
 * 
 * Bu fonksiyon, kullanıcının bir seçenek seçmesi durumunda
 * cevabı kaydeder ve bir sonraki soruya geçer.
 * 
 * Args:
 *     opt (string): Seçilen seçenek (genellikle "Yes" veya "No")
 * 
 * Yapılan İşlemler:
 * - Cevap answers listesine eklenir
 * - step bir artırılır
 * - askAgent() çağrılarak bir sonraki soru alınır
 */
function handleOption(opt) {
    answers.push(opt);
    step++;
    askAgent();
}

/**
 * Backend'den soru veya öneri alır.
 * 
 * Bu fonksiyon, mevcut adıma göre backend'e istek gönderir
 * ve gelen yanıtı işler. Soru varsa render eder, öneriler
 * varsa gösterir, hata varsa kullanıcıya bildirir.
 * 
 * İşlem Akışı:
 * 1. Loading göstergesi gösterilir
 * 2. /ask endpoint'ine POST isteği gönderilir
 * 3. Yanıt türüne göre işlenir:
 *    - question: renderQuestion() çağrılır
 *    - recommendations: renderRecommendations() çağrılır
 *    - error: Hata mesajı gösterilir
 * 
 * Global Değişkenler:
 * - step: Mevcut adım
 * - category: Seçilen kategori
 * - answers: Verilen cevaplar listesi
 */
function askAgent() {
    document.querySelector('.loading').style.display = '';
    document.querySelector('.error').textContent = '';
    // Show custom loading widget only when fetching recommendations
    let specs = window.currentSpecs && window.currentSpecs[category] ? window.currentSpecs[category] : [];
    if (step > specs.length) {
        showLoadingScreen();
    }
    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step, category, answers })
    })
    .then(res => res.json())
    .then(data => {
        if (data.question && data.options) {
            hideLoadingScreen();
            renderQuestion(data.question, data.options, data.emoji);
        } else if (data.recommendations) {
            renderRecommendations(data.recommendations);
        } else if (data.error) {
            hideLoadingScreen();
            document.querySelector('.loading').style.display = 'none';
            showNotification(data.error, 'error');
        }
    })
    .catch(err => {
        hideLoadingScreen();
        document.querySelector('.loading').style.display = 'none';
        showNotification('Sunucuya erişilemiyor: ' + err, 'error');
    });
}

/**
 * Sayfa yüklendiğinde çalışan ana fonksiyon (tekrar).
 * 
 * Bu fonksiyon, sayfa tamamen yüklendiğinde çalışır ve:
 * 1. Kategorileri backend'den yükler
 * 2. Kategori kartlarını render eder
 * 3. Event listener'ları ayarlar
 * 
 * Not: Bu fonksiyon dosyanın sonunda tekrar tanımlanmıştır.
 * İlk tanım yukarıda, bu ikinci tanım dosyanın sonunda.
 */
window.onload = () => {
    // Get categories and specs from backend
    fetch('/categories')
        .then(res => res.json())
        .then(data => {
            const categories = Object.keys(data);
            window.currentSpecs = {};
            for (const cat of categories) {
                window.currentSpecs[cat] = data[cat].specs || [];
            }
            renderLanding(categories);
        });
};

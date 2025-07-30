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
 * Kategori ikonları sözlüğü - Alışveriş odaklı ikonlar.
 * 
 * Her kategori için modern emoji ikonu tanımlar.
 * Eğer kategori bu listede yoksa, varsayılan olarak 🛍️ kullanılır.
 */
const categoryIcons = {
    'Mouse': '🖱️',
    'Headphones': '🎧',
    'Phone': '📱',
    'Laptop': '💻'
};

/**
 * Kategori renkleri - Alışveriş odaklı renk paleti.
 */
const categoryColors = {
    'Mouse': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'Headphones': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'Phone': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'Laptop': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
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
        
        // Kategori rengini uygula
        if (categoryColors[cat]) {
            card.style.background = categoryColors[cat];
            card.style.color = '#ffffff';
        }
        
        const icon = document.createElement('div');
        icon.className = 'category-icon';
        icon.textContent = categoryIcons[cat] || '🛍️';
        
        const label = document.createElement('div');
        label.className = 'category-label';
        label.textContent = cat;
        label.style.color = categoryColors[cat] ? '#ffffff' : '#2d3748';
        
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
 * Soru kartını render eder - Alışveriş odaklı tasarım.
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
 * - Gradient arka plan
 * - Emoji, soru metni ve seçenek butonları
 * - Responsive tasarım
 * - Hover efektleri
 */
function renderQuestion(question, options, emoji) {
    document.querySelector('.loading').style.display = 'none';
    const qDiv = document.querySelector('.question');
    qDiv.innerHTML = '';
    const card = document.createElement('div');
    card.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    card.style.borderRadius = '30px';
    card.style.boxShadow = '0 20px 40px rgba(0,0,0,0.15)';
    card.style.width = '500px';
    card.style.margin = '40px auto';
    card.style.padding = '50px 30px';
    card.style.display = 'flex';
    card.style.flexDirection = 'column';
    card.style.alignItems = 'center';
    card.style.justifyContent = 'center';
    card.style.position = 'relative';
    card.style.color = '#ffffff';
    card.style.backdropFilter = 'blur(10px)';
    
    // Emoji
    const emojiDiv = document.createElement('div');
    emojiDiv.style.fontSize = '4em';
    emojiDiv.style.marginBottom = '20px';
    emojiDiv.textContent = emoji || '🛍️';
    card.appendChild(emojiDiv);
    
    // Question
    const qText = document.createElement('div');
    qText.style.fontSize = '1.8em';
    qText.style.fontWeight = 'bold';
    qText.style.textAlign = 'center';
    qText.style.marginBottom = '30px';
    qText.style.lineHeight = '1.4';
    qText.textContent = question;
    card.appendChild(qText);
    
    // Options
    const optionsDiv = document.createElement('div');
    optionsDiv.style.display = 'flex';
    optionsDiv.style.gap = '30px';
    optionsDiv.style.flexWrap = 'wrap';
    optionsDiv.style.justifyContent = 'center';
    
    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.textContent = opt === 'Yes' ? '✅ Evet' : '❌ Hayır';
        btn.style.padding = '15px 40px';
        btn.style.fontSize = '1.2em';
        btn.style.borderRadius = '50px';
        btn.style.border = 'none';
        btn.style.cursor = 'pointer';
        btn.style.background = opt === 'Yes' ? 'linear-gradient(45deg, #43e97b, #38f9d7)' : 'linear-gradient(45deg, #ff6b6b, #feca57)';
        btn.style.color = '#ffffff';
        btn.style.fontWeight = '600';
        btn.style.boxShadow = '0 8px 25px rgba(0,0,0,0.2)';
        btn.style.transition = 'all 0.3s ease';
        btn.onclick = () => handleOption(opt);
        btn.onmouseenter = () => {
            btn.style.transform = 'translateY(-3px)';
            btn.style.boxShadow = '0 12px 30px rgba(0,0,0,0.3)';
        };
        btn.onmouseleave = () => {
            btn.style.transform = 'translateY(0)';
            btn.style.boxShadow = '0 8px 25px rgba(0,0,0,0.2)';
        };
        optionsDiv.appendChild(btn);
    });
    card.appendChild(optionsDiv);
    qDiv.appendChild(card);
    document.querySelector('.recommendation').innerHTML = '';
    document.querySelector('.error').textContent = '';
}

/**
 * Ürün önerilerini render eder - Alışveriş odaklı tasarım.
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
            <h2 style="font-size: 2.5em; color: #ffffff; margin-bottom: 20px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                🎉 Önerilen Ürünler
            </h2>
            <p style="color: #ffffff; font-size: 1.2em; opacity: 0.9;">
                Size en uygun ürünleri bulduk!
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
            linkHtml = ` <a href="${url}" target="_blank" style="color:#ffffff; text-decoration:none; background:linear-gradient(45deg, #ff6b6b, #feca57); padding:8px 16px; border-radius:20px; font-weight:600; margin-left:10px;">🛒 Satın Al</a>`;
        }
        
        html += `
            <div style="
                background: rgba(255,255,255,0.95);
                margin-bottom: 20px;
                padding: 25px;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 15px;
            ">
                <div style="flex: 1; min-width: 200px;">
                    <div style="font-size: 1.3em; font-weight: 600; color: #2d3748; margin-bottom: 8px;">
                        ${r.name}
                    </div>
                    <div style="font-size: 1.1em; color: #ff6b6b; font-weight: 600;">
                        💰 ${r.price}
                    </div>
                </div>
                ${linkHtml}
            </div>
        `;
    });
    
    html += `
        <div style="text-align: center; margin-top: 40px;">
            <button id="back-to-categories" style="
                padding: 18px 40px;
                font-size: 1.2em;
                border-radius: 50px;
                border: none;
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: #ffffff;
                cursor: pointer;
                font-weight: 600;
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            ">🔄 Yeni Arama Yap</button>
        </div>
    `;
    
    recDiv.innerHTML = html;
    document.querySelector('.error').textContent = '';
    
    // Back button hover effect
    const backBtn = document.getElementById('back-to-categories');
    if (backBtn) {
        backBtn.onmouseenter = () => {
            backBtn.style.transform = 'translateY(-3px)';
            backBtn.style.boxShadow = '0 12px 30px rgba(0,0,0,0.3)';
        };
        backBtn.onmouseleave = () => {
            backBtn.style.transform = 'translateY(0)';
            backBtn.style.boxShadow = '0 8px 25px rgba(0,0,0,0.2)';
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
        padding: 15px 25px;
        border-radius: 10px;
        color: #ffffff;
        font-weight: 600;
        z-index: 10000;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
    `;
    
    const colors = {
        'error': 'linear-gradient(45deg, #ff6b6b, #feca57)',
        'warning': 'linear-gradient(45deg, #feca57, #ff9ff3)',
        'success': 'linear-gradient(45deg, #43e97b, #38f9d7)',
        'info': 'linear-gradient(45deg, #4facfe, #00f2fe)'
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
 * Tam ekran loading ekranını gösterir - Alışveriş odaklı tasarım.
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
            background: rgba(102, 126, 234, 0.9);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(10px);
        `;
        loadingDiv.innerHTML = `
            <div style="margin-bottom: 30px;">
                <div style="
                    width: 80px;
                    height: 80px;
                    border: 8px solid rgba(255,255,255,0.3);
                    border-top: 8px solid #ffffff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                "></div>
            </div>
            <div style="font-size: 1.5em; color: #ffffff; font-weight: 600; text-align: center;">
                🛍️ Ürünler aranıyor...
            </div>
            <div style="font-size: 1.1em; color: rgba(255,255,255,0.8); margin-top: 10px; text-align: center;">
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

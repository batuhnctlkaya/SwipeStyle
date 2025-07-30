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
            alert(data.error);
        } else {
            alert('Kategori tespit edilemedi veya oluşturulamadı. Lütfen daha açık bir istek girin.');
        }
    })
    .catch(() => {
        hideLoadingScreen();
        alert('Sunucuya erişilemiyor. Lütfen daha sonra tekrar deneyin.');
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
 * Kategori ikonları sözlüğü.
 * 
 * Her kategori için emoji ikonu tanımlar.
 * Eğer kategori bu listede yoksa, varsayılan olarak 🔍 kullanılır.
 */
const categoryIcons = {
    'Mouse': '🖱️',
    'Headphones': '🎧',
    'Phone': '📱',
    'Laptop': '💻'
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
 * Soru kartını render eder.
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
    card.style.background = 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)';
    card.style.borderRadius = '24px';
    card.style.boxShadow = '0 4px 24px rgba(0,0,0,0.10)';
    card.style.width = '400px';
    card.style.margin = '40px auto';
    card.style.padding = '40px 20px';
    card.style.display = 'flex';
    card.style.flexDirection = 'column';
    card.style.alignItems = 'center';
    card.style.justifyContent = 'center';
    card.style.position = 'relative';
    // Emoji
    const emojiDiv = document.createElement('div');
    emojiDiv.style.fontSize = '3em';
    emojiDiv.style.marginBottom = '18px';
    emojiDiv.textContent = emoji || '';
    card.appendChild(emojiDiv);
    // Question
    const qText = document.createElement('div');
    qText.style.fontSize = '1.6em';
    qText.style.fontWeight = 'bold';
    qText.style.textAlign = 'center';
    qText.style.marginBottom = '18px';
    qText.textContent = question;
    card.appendChild(qText);
    // Options
    const optionsDiv = document.createElement('div');
    optionsDiv.style.display = 'flex';
    optionsDiv.style.gap = '24px';
    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.textContent = opt;
        btn.style.padding = '12px 32px';
        btn.style.fontSize = '1.1em';
        btn.style.borderRadius = '12px';
        btn.style.border = 'none';
        btn.style.cursor = 'pointer';
        btn.style.background = '#fff';
        btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
        btn.onclick = () => handleOption(opt);
        optionsDiv.appendChild(btn);
    });
    card.appendChild(optionsDiv);
    qDiv.appendChild(card);
    document.querySelector('.recommendation').innerHTML = '';
    document.querySelector('.error').textContent = '';
}

/**
 * Ürün önerilerini render eder.
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
    let html = '<h2>Önerilen Ürünler</h2>' + recs.map(r => {
        let linkHtml = '';
        let url = r.link || '';
        if (url && !url.startsWith('http') && url.length > 5) {
            url = 'https://' + url.replace(/^(www\.)?/, '');
        }
        if (url && url.startsWith('http')) {
            linkHtml = ` <a href="${url}" target="_blank" style="color:#3b82f6; text-decoration:underline;">Satın Al</a>`;
        }
        return `<div style="margin-bottom:18px;">${r.name} - ${r.price}${linkHtml}</div>`;
    }).join('');
    html += `<div style="margin-top:32px;text-align:center;"><button id="back-to-categories" style="padding:12px 32px;font-size:1.1em;border-radius:12px;border:none;background:#a18cd1;color:#fff;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.08);">Yeni arama yap</button></div>`;
    recDiv.innerHTML = html;
    document.querySelector('.error').textContent = '';
    document.getElementById('back-to-categories').onclick = () => {
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

/**
 * Tam ekran loading ekranını gösterir.
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
        loadingDiv.style.position = 'fixed';
        loadingDiv.style.top = '0';
        loadingDiv.style.left = '0';
        loadingDiv.style.width = '100vw';
        loadingDiv.style.height = '100vh';
        loadingDiv.style.background = 'rgba(250,251,252,0.85)';
        loadingDiv.style.display = 'flex';
        loadingDiv.style.flexDirection = 'column';
        loadingDiv.style.alignItems = 'center';
        loadingDiv.style.justifyContent = 'center';
        loadingDiv.style.zIndex = '9999';
        loadingDiv.innerHTML = `
            <div style="margin-bottom:24px;">
                <div style="width:64px;height:64px;border:8px solid #e0e0e0;border-top:8px solid #a18cd1;border-radius:50%;animation:spin 1s linear infinite;"></div>
            </div>
            <div style="font-size:1.3em;color:#6c6c6c;">Ürünler aranıyor, lütfen bekleyin...</div>
            <style>
            @keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }
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
            document.querySelector('.error').textContent = data.error;
        }
    })
    .catch(err => {
        hideLoadingScreen();
        document.querySelector('.loading').style.display = 'none';
        document.querySelector('.error').textContent = 'Sunucuya erişilemiyor: ' + err;
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

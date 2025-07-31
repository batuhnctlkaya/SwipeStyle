<<<<<<< HEAD
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
=======
// Main.js'e CSS stillerini ekleyin veya ayrı bir CSS dosyası oluşturun

const tooltipStyles = `
<style>
.question-container {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    width: 100%;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.question-container h2 {
    display: inline-block;
    margin-right: 10px;
    flex: 1;
}

.tooltip-container {
    position: relative;
    display: inline-block;
    margin-left: 5px;
    z-index: 10;
}

.info-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    cursor: help;
    opacity: 0.8;
    transition: all 0.3s ease;
    user-select: none;
    padding: 4px;
    border-radius: 50%;
    background-color: #f0f0f0;
    width: 22px;
    height: 22px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    border: 1px solid #e0e0e0;
}

.info-icon:hover {
    opacity: 1;
    transform: scale(1.1);
    background-color: #e6e6e6;
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}

.tooltip-text {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    background-color: #333;
    color: white;
    text-align: left;
    padding: 14px;
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.5;
    width: 300px;
    z-index: 1000;
    transition: opacity 0.3s ease, visibility 0.3s ease;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    word-wrap: break-word;
    border-left: 4px solid #a18cd1;
}

.tooltip-text::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -6px;
    border-width: 6px;
    border-style: solid;
    border-color: #333 transparent transparent transparent;
}

/* Mobil cihazlar için özel düzenlemeler */
@media (max-width: 768px) {
    .question-container {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
        padding: 0 10px;
    }
    
    .tooltip-container {
        margin-top: -5px;
        align-self: flex-start;
    }
    
    .tooltip-text {
        width: 280px;
        left: 0;
        transform: none;
        bottom: 140%;
        font-size: 13px;
        padding: 12px;
    }
    
    .tooltip-text::after {
        left: 10px;
        margin-left: 0;
    }
    
    .info-icon {
        font-size: 16px;
    }
}

/* Çok küçük ekranlar için */
@media (max-width: 480px) {
    .tooltip-text {
        width: calc(100vw - 40px);
        max-width: 280px;
        left: -10px;
        font-size: 12px;
        padding: 10px;
    }
}

/* Tooltip animasyonları */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.tooltip-text.show {
    visibility: visible;
    opacity: 1;
    animation: fadeIn 0.3s ease;
}

/* Options container */
.options-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    padding: 0 10px;
}

/* Option butonları için iyileştirmeler */
.option-btn {
    margin: 6px 0;
    padding: 14px 18px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    background: white;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 15px;
    line-height: 1.4;
    text-align: left;
    position: relative;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    font-weight: 500;
    color: #333;
}

.option-btn:hover {
    background: #f9f9f9;
    border-color: #a18cd1;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.option-btn:active {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.option-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

@media (max-width: 768px) {
    .option-btn {
        width: 100%;
        margin: 5px 0;
        padding: 16px 18px;
        font-size: 16px;
    }
}

/* İnteraksiyon konteynerinde iyileştirmeler */
#interaction {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px 10px;
}

.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    color: #666;
    font-size: 16px;
}

.error {
    background-color: #ffebee;
    color: #d32f2f;
    padding: 12px;
    border-radius: 8px;
    margin-top: 20px;
    border-left: 4px solid #d32f2f;
    font-size: 14px;
}
</style>`;

// Sayfaya CSS ekle
document.head.insertAdjacentHTML('beforeend', tooltipStyles);

// Chatbox logic
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
function handleChatboxEntry() {
    const input = document.getElementById('chatbox-input').value.trim();
    if (!input) return;
    showLoadingScreen();
<<<<<<< HEAD
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
=======
    
    // Yeni search API'sini kullan
    fetch(`/search/${encodeURIComponent(input)}`)
    .then(res => res.json())
    .then(data => {
        hideLoadingScreen();
        
        if (data.status === 'error') {
            alert("Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.");
            return;
        }
        
        let categoryName = '';
        
        // API yanıt durumuna göre farklı işlemler
        switch(data.status) {
            case 'found':
                categoryName = data.category;
                break;
                
            case 'similar_found':
            case 'partial_match':
                categoryName = data.matched_category;
                alert(`"${input}" aramanız "${categoryName}" kategorisiyle eşleştirildi.`);
                break;
                
            case 'alias_match':
                categoryName = data.matched_category;
                alert(`"${input}" aramanız "${categoryName}" kategorisine yönlendirildi.`);
                break;
                
            case 'created':
                categoryName = data.category;
                alert(`"${categoryName}" için yeni bir kategori oluşturuldu.`);
                break;
                
            default:
                // Fallback - eski metodu kullan
                fetch('/detect_category', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: input })
                })
                .then(res => res.json())
                .then(categoryData => {
                    if (categoryData.category) {
                        category = categoryData.category;
                        step = 1;
                        answers = [];
                        document.querySelector('.landing').style.display = 'none';
                        document.getElementById('interaction').style.display = '';
                        askAgent();
                    } else {
                        alert('Aradığınız kategoriyi bulamadım. Lütfen başka bir şey deneyin.');
                    }
                });
                return;
        }
        
        if (categoryName) {
            category = categoryName;
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
            step = 1;
            answers = [];
            document.querySelector('.landing').style.display = 'none';
            document.getElementById('interaction').style.display = '';
            askAgent();
<<<<<<< HEAD
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
=======
        }
    })
    .catch(error => {
        console.error("Arama hatası:", error);
        hideLoadingScreen();
        alert("Bir hata oluştu, lütfen tekrar deneyin.");
    });
}

// Bu window.onload sonraki ile çakıştığı için kaldırılacak

let step = 0;
let category = null;
let answers = [];

>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
const categoryIcons = {
    'Mouse': '🖱️',
    'Headphones': '🎧',
    'Phone': '📱',
    'Laptop': '💻'
};

<<<<<<< HEAD
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
=======
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
function renderLanding(categories) {
    const grid = document.getElementById('category-cards');
    grid.innerHTML = '';
    categories.forEach(cat => {
        const card = document.createElement('div');
        card.className = 'category-card';
        card.onclick = () => startInteraction(cat);
<<<<<<< HEAD
        
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
        
=======
        const icon = document.createElement('div');
        icon.className = 'category-icon';
        icon.textContent = categoryIcons[cat] || '🔍';
        const label = document.createElement('div');
        label.className = 'category-label';
        label.textContent = cat;
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
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

<<<<<<< HEAD
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
=======
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
function startInteraction(selectedCategory) {
    category = selectedCategory;
    step = 1;
    answers = [];
    document.querySelector('.landing').style.display = 'none';
    document.getElementById('interaction').style.display = '';
    askAgent();
}

<<<<<<< HEAD
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
=======
function renderQuestion(question, options, emoji) {
    const interaction = document.getElementById('interaction');
    
    console.log("Rendering question:", question);
    console.log("With tooltip:", window.currentQuestionTooltip);
    
    // İlk önce soru ve seçenekleri temizle
    const questionDiv = interaction.querySelector('.question');
    const optionsDiv = interaction.querySelector('.options');
    
    if (!questionDiv || !optionsDiv) {
        console.error("Question or options div not found!");
        document.querySelector('.error').textContent = 'Sayfa yapısında sorun var. Lütfen sayfayı yenileyin.';
        return;
    }
    
    questionDiv.innerHTML = '';
    optionsDiv.innerHTML = '';
    
    // Soru container'ını oluştur
    const questionContainer = document.createElement('div');
    questionContainer.className = 'question-container';
    
    // Soru başlığı
    const questionTitle = document.createElement('h2');
    questionTitle.innerHTML = `${emoji} ${question}`;
    questionContainer.appendChild(questionTitle);
    
    // Tooltip varsa ekle
    if (window.currentQuestionTooltip) {
        const tooltipContainer = document.createElement('div');
        tooltipContainer.className = 'tooltip-container';
        
        const infoIcon = document.createElement('span');
        infoIcon.className = 'info-icon';
        infoIcon.textContent = 'ℹ️';
        infoIcon.addEventListener('mouseover', showTooltip);
        infoIcon.addEventListener('mouseout', hideTooltip);
        
        const tooltipText = document.createElement('div');
        tooltipText.className = 'tooltip-text';
        tooltipText.id = 'tooltip';
        tooltipText.innerHTML = window.currentQuestionTooltip;
        
        tooltipContainer.appendChild(infoIcon);
        tooltipContainer.appendChild(tooltipText);
        questionContainer.appendChild(tooltipContainer);
    }
    
    // Seçenekleri oluştur
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'options-container';
    
    options.forEach(opt => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        button.textContent = opt;
        button.addEventListener('click', function() {
            handleOption(opt);
        });
        optionsContainer.appendChild(button);
    });
    
    // Soru ve seçenekleri ekle
    questionDiv.appendChild(questionContainer);
    optionsDiv.appendChild(optionsContainer);
    
    // Loading'i gizle ve interaction'ı göster
    const loadingDiv = interaction.querySelector('.loading');
    if (loadingDiv) loadingDiv.style.display = 'none';
    
    interaction.style.display = 'block';
    
    console.log("Question rendered successfully");
}

function showTooltip(event) {
    console.log("Tooltip gösteriliyor...");
    
    // Event hedefinin tooltip container'ını bul
    const infoIcon = event.currentTarget;
    const tooltipContainer = infoIcon.parentElement;
    const tooltip = tooltipContainer.querySelector('.tooltip-text');
    
    if (tooltip) {
        // Class kullanarak tooltip'i göster
        tooltip.classList.add('show');
        tooltip.style.visibility = 'visible';
        tooltip.style.opacity = '1';
        
        // Tooltip konumunu hesapla
        const iconRect = infoIcon.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        // Ekranın sağ kenarında olup olmadığını kontrol et
        const rightEdgeDistance = window.innerWidth - (iconRect.right + tooltipRect.width/2);
        if (rightEdgeDistance < 0) {
            tooltip.style.left = 'auto';
            tooltip.style.right = '0';
            tooltip.style.transform = 'translateX(0)';
        }
        
        // Ekranın üst kısmında olup olmadığını kontrol et
        if (iconRect.top < tooltipRect.height + 20) {
            tooltip.style.bottom = 'auto';
            tooltip.style.top = '130%';
            
            // Ok yönünü değiştir
            tooltip.style.setProperty('--arrow-direction', 'up');
        }
        
        console.log("Tooltip gösterildi");
        
        // Tooltip dışında bir yere tıklanırsa tooltip'i gizle
        document.addEventListener('click', closeTooltipOnClickOutside);
        
    } else {
        console.log("Tooltip bulunamadı");
    }
    
    // Event'in daha fazla yayılmasını engelle
    event.stopPropagation();
}

// Tooltip dışında bir yere tıklandığında tooltip'i kapatır
function closeTooltipOnClickOutside(event) {
    const tooltips = document.querySelectorAll('.tooltip-text.show');
    if (tooltips.length > 0) {
        let clickedOnTooltip = false;
        
        tooltips.forEach(tooltip => {
            if (tooltip.contains(event.target) || event.target.classList.contains('info-icon')) {
                clickedOnTooltip = true;
            }
        });
        
        if (!clickedOnTooltip) {
            hideTooltip();
            document.removeEventListener('click', closeTooltipOnClickOutside);
        }
    } else {
        document.removeEventListener('click', closeTooltipOnClickOutside);
    }
}

function hideTooltip(event) {
    console.log("Tooltip gizleniyor...");
    
    // Event hedefinin tooltip container'ını bul
    if (event && event.currentTarget) {
        const infoIcon = event.currentTarget;
        const tooltipContainer = infoIcon.parentElement;
        const tooltip = tooltipContainer.querySelector('.tooltip-text');
        
        if (tooltip) {
            tooltip.classList.remove('show');
            tooltip.style.visibility = 'hidden';
            tooltip.style.opacity = '0';
        }
    } else {
        // Eğer event yoksa (veya event.target yoksa) tüm tooltipleri gizle
        const tooltips = document.querySelectorAll('.tooltip-text');
        tooltips.forEach(tooltip => {
            tooltip.classList.remove('show');
            tooltip.style.visibility = 'hidden';
            tooltip.style.opacity = '0';
        });
    }
    
    console.log("Tooltip gizlendi");
}

// Bu fonksiyon ikinci tanımlanışı ile çakışıyor, kaldırılacak

function renderRecommendations(recs) {
    hideLoadingScreen();
    const recDiv = document.querySelector('.recommendation');
    let html = '<h2>Önerilen Ürünler</h2>' + recs.map(r => {
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
        let linkHtml = '';
        let url = r.link || '';
        if (url && !url.startsWith('http') && url.length > 5) {
            url = 'https://' + url.replace(/^(www\.)?/, '');
        }
        if (url && url.startsWith('http')) {
<<<<<<< HEAD
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
=======
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

>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
function showLoadingScreen() {
    hideLoadingScreen();
    const interaction = document.getElementById('interaction');
    let loadingDiv = document.getElementById('custom-loading');
    if (!loadingDiv) {
        loadingDiv = document.createElement('div');
        loadingDiv.id = 'custom-loading';
<<<<<<< HEAD
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
=======
        loadingDiv.className = 'loading-container';
        loadingDiv.innerHTML = `
            <div class="ai-brain">
                <div class="neural-ring"></div>
                <div class="neural-ring"></div>
                <div class="neural-ring"></div>
                <div class="ai-core"></div>
            </div>
            <div class="loading-text">AI İşliyor...</div>
            <div class="loading-subtext">Yapay zeka tercihlerinizi analiz ediyor ve size en uygun ürünleri buluyor. Bu işlem 10-45 saniye sürebilir.</div>
            <div class="progress-container">
                <div class="progress-bar" id="ai-progress" style="width: 0%"></div>
            </div>
            <button class="emergency-reset" id="emergency-reset">
                Çok Uzun Sürüyor mu? Sıfırla
            </button>
        `;
        
        // Acil durum sıfırlama butonu
        const resetButton = loadingDiv.querySelector('#emergency-reset');
        resetButton.onclick = () => {
            isRequestInProgress = false;
            hideLoadingScreen();
            document.getElementById('interaction').style.display = 'none';
            document.querySelector('.landing').style.display = '';
            document.querySelector('.recommendation').innerHTML = '';
            document.querySelector('.error').textContent = '';
            step = 0;
            category = null;
            answers = [];
            window.currentQuestionTooltip = null;
        };
        
        document.body.appendChild(loadingDiv);
    }
    
    // Start progress animation
    loadingDiv.style.display = 'flex';
    animateProgress();
}

function animateProgress() {
    const progressBar = document.getElementById('ai-progress');
    if (!progressBar) return;
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 3 + 1; // Random increment between 1-4
        if (progress > 90) progress = 90; // Don't go to 100% until actually done
        
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
        // Complete the progress bar before hiding
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

// Flag to track if a request is in progress
let isRequestInProgress = false;

function handleOption(opt) {
    // Prevent multiple clicks while a request is in progress
    if (isRequestInProgress) {
        console.log("Request already in progress, ignoring click");
        return;
    }
    
    console.log("Option selected:", opt);
    
    try {
        // Set the flag to indicate a request is in progress
        isRequestInProgress = true;
        
        // Disable all option buttons to prevent further clicks
        const optionButtons = document.querySelectorAll('.option-btn');
        optionButtons.forEach(btn => {
            btn.disabled = true;
            btn.style.opacity = '0.5';
            btn.style.cursor = 'not-allowed';
        });
        
        // Seçimi görsel olarak göster
        const selectedButton = Array.from(optionButtons).find(btn => btn.textContent === opt);
        if (selectedButton) {
            selectedButton.style.backgroundColor = '#f0f0ff';
            selectedButton.style.borderColor = '#a18cd1';
        }
        
        // Cevabı kaydet ve bir sonraki adıma geç
        answers.push(opt);
        step++;
        
        // Error göstergesini temizle
        document.querySelector('.error').textContent = '';
        
        console.log("İlerliyor: Adım", step, "Cevaplar:", answers);
        
        // Kısa bir gecikme ile askAgent'i çağır (animasyon için)
        setTimeout(function() {
            askAgent();
        }, 300);
    } catch(e) {
        console.error("handleOption'da hata:", e);
        isRequestInProgress = false;
        document.querySelector('.error').textContent = 'İşlem sırasında bir hata oluştu. Lütfen sayfayı yenileyin.';
    }
}

function askAgent() {
    console.log(`Soru soruluyor: Step ${step}, Category ${category}, Answers:`, answers);
    
    // İstek devam ediyor kontrolünü kaldırdım çünkü handleOption zaten kontrol ediyor
    
    document.querySelector('.error').textContent = '';
    
    // Loading ekranını göster
    const loadingElement = document.querySelector('.loading');
    if (loadingElement) {
        loadingElement.style.display = 'block';
        loadingElement.textContent = 'Yükleniyor...';
    }
    
    // Debug için mevcut durumu konsola yazdır
    console.log("İstek başlatılıyor:", {
        step: step,
        category: category,
        answers: answers,
        isRequestInProgress: isRequestInProgress
    });
    
    // Tavsiyeler alınırken özel yükleme ekranını göster
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
    let specs = window.currentSpecs && window.currentSpecs[category] ? window.currentSpecs[category] : [];
    if (step > specs.length) {
        showLoadingScreen();
    }
<<<<<<< HEAD
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
=======
    
    // 45 saniye zaman aşımı ekle (AI işlemleri için uzatıldı)
    const timeoutId = setTimeout(() => {
        if (isRequestInProgress) {
            console.log("Zaman aşımı oluştu!");
            isRequestInProgress = false;
            hideLoadingScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            document.querySelector('.error').textContent = 'İstek zaman aşımına uğradı. AI analizi uzun sürdü, lütfen tekrar deneyin.';
        }
    }, 45000);
    
    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            step: step, 
            category: category, 
            answers: answers,
            language: 'tr' // Türkçe dilini varsayılan olarak kullan
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
        
        // Debugging: Log the exact structure of the data object
        console.log("Response has question:", !!data.question);
        console.log("Response has options:", !!data.options);
        console.log("Response has recommendations:", !!data.recommendations);
        console.log("Response has error:", !!data.error);
        console.log("Response keys:", Object.keys(data));
        
        if (data.question && data.options) {
            hideLoadingScreen();
            // Tooltip bilgisini global değişkene kaydet
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
            // Handle unexpected response format without infinite loop
            console.error('Beklenmeyen yanıt formatı:', data);
            hideLoadingScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            document.querySelector('.error').textContent = 'Beklenmeyen bir yanıt alındı. Lütfen sayfayı yenileyin.';
        }
    })
    .catch(err => {
        clearTimeout(timeoutId);  // Zaman aşımını iptal et
        // Reset the request in progress flag even if there's an error
        isRequestInProgress = false;
        
        hideLoadingScreen();
        if (loadingElement) loadingElement.style.display = 'none';
        document.querySelector('.error').textContent = 'Sunucuya erişilemiyor: ' + err.message;
        console.error('Hata:', err);
    });
}

window.onload = () => {
    console.log("SwipeStyle uygulaması başlatılıyor...");
    
    // Sayfaya CSS ekle
    document.head.insertAdjacentHTML('beforeend', tooltipStyles);
    
    // CSS keyframes için animasyon tanımı ekle
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `);
    
    // Get categories and specs from backend
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
            
            // Kategori ve spec bilgilerini kaydet
            for (const cat of categories) {
                window.currentSpecs[cat] = data[cat].specs || [];
            }
            
            renderLanding(categories);
            
            // Chatbox event listeners
            const chatboxSend = document.getElementById('chatbox-send');
            const chatboxInput = document.getElementById('chatbox-input');
            
            if (chatboxSend && chatboxInput) {
                chatboxSend.onclick = handleChatboxEntry;
                chatboxInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') handleChatboxEntry();
                });
            }
            
            // Sayfa başına sıfırlama düğmesi ekle
            const loadingElement = document.querySelector('.loading');
            if (loadingElement) {
                loadingElement.innerHTML += '<button id="reset-app" style="margin-top:20px;padding:8px 16px;background:#f44336;color:white;border:none;border-radius:6px;cursor:pointer;">İşlemi Sıfırla</button>';
                document.getElementById('reset-app').onclick = () => {
                    isRequestInProgress = false;
                    hideLoadingScreen();
                    loadingElement.style.display = 'none';
                    document.getElementById('interaction').style.display = 'none';
                    document.querySelector('.landing').style.display = '';
                    document.querySelector('.question').innerHTML = '';
                    document.querySelector('.options').innerHTML = '';
                    step = 0;
                    category = null;
                    answers = [];
                    window.currentQuestionTooltip = null;
                    console.log("Uygulama sıfırlandı");
                };
            }
            
            console.log("SwipeStyle başarıyla başlatıldı");
        })
        .catch(error => {
            console.error("Kategoriler yüklenirken hata oluştu:", error);
            document.querySelector('.error').textContent = "Kategoriler yüklenemedi. Lütfen sayfayı yenileyin.";
>>>>>>> 08f17ad2d7a03b3f8177b4196993bc2448082886
        });
};

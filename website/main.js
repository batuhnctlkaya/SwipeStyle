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
function handleChatboxEntry() {
    const input = document.getElementById('chatbox-input').value.trim();
    if (!input) return;
    showLoadingScreen();
    fetch('/detect_category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
    })
    .then(res => res.json())
    .then(data => {
        hideLoadingScreen();
        if (data.category) {
            category = data.category;
            step = 1;
            answers = [];
            document.querySelector('.landing').style.display = 'none';
            document.getElementById('interaction').style.display = '';
            askAgent();
        } else {
            alert('Could not determine a product category. Please try again.');
        }
    })
    .catch(() => {
        hideLoadingScreen();
        alert('Could not process your request.');
    });
}

// Bu window.onload sonraki ile çakıştığı için kaldırılacak

let step = 0;
let category = null;
let answers = [];

const categoryIcons = {
    'Mouse': '🖱️',
    'Headphones': '🎧',
    'Phone': '📱',
    'Laptop': '💻'
};

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

function startInteraction(selectedCategory) {
    category = selectedCategory;
    step = 1;
    answers = [];
    document.querySelector('.landing').style.display = 'none';
    document.getElementById('interaction').style.display = '';
    askAgent();
}

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
            <div style="font-size:18px;font-weight:500;color:#666;margin-bottom:20px;">Düşünüyorum...</div>
            <button id="emergency-reset" style="margin-top:20px;padding:8px 16px;background:#dc3545;color:white;border:none;border-radius:6px;cursor:pointer;font-size:14px;">
                Takıldı mı? Sıfırla
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
    loadingDiv.style.display = 'flex';
}

function hideLoadingScreen() {
    let loadingDiv = document.getElementById('custom-loading');
    if (loadingDiv) loadingDiv.style.display = 'none';
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
    let specs = window.currentSpecs && window.currentSpecs[category] ? window.currentSpecs[category] : [];
    if (step > specs.length) {
        showLoadingScreen();
    }
    
    // 15 saniye zaman aşımı ekle
    const timeoutId = setTimeout(() => {
        if (isRequestInProgress) {
            console.log("Zaman aşımı oluştu!");
            isRequestInProgress = false;
            hideLoadingScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            document.querySelector('.error').textContent = 'İstek zaman aşımına uğradı. Lütfen sayfayı yenileyin.';
        }
    }, 15000);
    
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
            // Try to recover by asking for the next question
            console.error('Beklenmeyen yanıt formatı:', data);
            hideLoadingScreen();
            if (loadingElement) loadingElement.style.display = 'none';
            
            // Try to continue anyway
            if (step > 0) {
                console.log("Bir sonraki adıma geçmeye çalışılıyor...");
                step++; // Try to move to next step
                setTimeout(() => {
                    askAgent(); // Try again with next step
                }, 500);
            } else {
                document.querySelector('.error').textContent = 'Beklenmeyen bir yanıt alındı. Lütfen sayfayı yenileyin.';
            }
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
        });
};

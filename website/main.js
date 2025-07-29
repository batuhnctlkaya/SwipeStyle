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
            <div style="font-size:1.3em;color:#6c6c6c;">Ürünler aranıyor, lütfen bekleyin...</div>
            <style>
            @keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }
            </style>
        `;
        document.body.appendChild(loadingDiv);
    }
    loadingDiv.style.display = 'flex';
}

function hideLoadingScreen() {
    let loadingDiv = document.getElementById('custom-loading');
    if (loadingDiv) loadingDiv.style.display = 'none';
}

function handleOption(opt) {
    answers.push(opt);
    step++;
    askAgent();
}

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

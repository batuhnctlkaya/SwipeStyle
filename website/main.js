let step = 0;
let category = null;
let answers = [];

function renderQuestion(question, options) {
    document.querySelector('.loading').style.display = 'none';
    document.querySelector('.question').textContent = question;
    const optionsDiv = document.querySelector('.options');
    optionsDiv.innerHTML = '';
    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.textContent = opt;
        btn.onclick = () => handleOption(opt);
        optionsDiv.appendChild(btn);
    });
    document.querySelector('.recommendation').innerHTML = '';
    document.querySelector('.error').textContent = '';
}

function renderRecommendations(recs) {
    document.querySelector('.loading').style.display = 'none';
    const recDiv = document.querySelector('.recommendation');
    recDiv.innerHTML = '<h2>Önerilen Ürünler</h2>' + recs.map(r => `<div>${r.name} - ${r.price}</div>`).join('');
    document.querySelector('.error').textContent = '';
}

function handleOption(opt) {
    if (step === 0) {
        category = opt;
        step = 1;
    } else if (step === 1) {
        answers.push(opt);
        step = 2;
    }
    askAgent();
}

function askAgent() {
    document.querySelector('.loading').style.display = '';
    document.querySelector('.error').textContent = '';
    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step, category, answers })
    })
    .then(res => res.json())
    .then(data => {
        if (data.question && data.options) {
            renderQuestion(data.question, data.options);
        } else if (data.recommendations) {
            renderRecommendations(data.recommendations);
        } else if (data.error) {
            document.querySelector('.loading').style.display = 'none';
            document.querySelector('.error').textContent = data.error;
        }
    })
    .catch(err => {
        document.querySelector('.loading').style.display = 'none';
        document.querySelector('.error').textContent = 'Sunucuya erişilemiyor: ' + err;
    });
}

window.onload = () => {
    document.querySelector('.loading').style.display = '';
    askAgent();
};

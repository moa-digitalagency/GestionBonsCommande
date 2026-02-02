// BTP Commande - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('[class*="bg-green-100"], [class*="bg-red-100"], [class*="bg-yellow-100"], [class*="bg-blue-100"]');
    flashMessages.forEach(function(msg) {
        if (msg.closest('.fixed')) {
            setTimeout(function() {
                msg.style.transition = 'opacity 0.5s';
                msg.style.opacity = '0';
                setTimeout(function() {
                    msg.remove();
                }, 500);
            }, 5000);
        }
    });

    // Confirm before delete actions
    document.querySelectorAll('form[onsubmit*="confirm"]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir effectuer cette action ?')) {
                e.preventDefault();
            }
        });
    });

    // Auto-resize textareas
    document.querySelectorAll('textarea').forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
});

// Product search functionality
function searchProducts(query) {
    if (query.length < 2) return;
    
    fetch('/products/search?q=' + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            console.log('Products found:', data);
        });
}

// Translation lookup
function lookupTranslation(term, targetLang) {
    return fetch('/lexique/search?q=' + encodeURIComponent(term) + '&lang=' + targetLang)
        .then(response => response.json());
}

// Format number with spaces (French style)
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// Format currency (MAD)
function formatCurrency(amount) {
    return formatNumber(parseFloat(amount).toFixed(2)) + ' MAD';
}

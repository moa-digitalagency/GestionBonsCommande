document.addEventListener('alpine:initialized', () => {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

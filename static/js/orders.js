function selectProduct(select) {
    const option = select.options[select.selectedIndex];
    if (option.value) {
        document.getElementById('description').value = option.dataset.label || '';
        document.getElementById('unit').value = option.dataset.unit || 'unite';
        if (option.dataset.price) {
            document.getElementById('unit_price').value = option.dataset.price;
        }
    }
}

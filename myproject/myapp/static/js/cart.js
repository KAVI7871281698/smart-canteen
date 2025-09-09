document.addEventListener('DOMContentLoaded', function() {
    // Quantity controls
    document.querySelectorAll('.quantity-control').forEach(control => {
        control.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-input');
            let value = parseInt(input.value);
            
            if (this.classList.contains('quantity-minus') && value > 1) {
                input.value = value - 1;
            } else if (this.classList.contains('quantity-plus')) {
                input.value = value + 1;
            }
        });
    });

    // Add to cart buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            const quantity = document.getElementById(`quantity-${itemId}`).value || 1;
            
            fetch('{% url "add_to_cart" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `item_id=${itemId}&quantity=${quantity}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart count in navbar
                    const cartCount = document.getElementById('cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.cart_total;
                    }
                    // Show success message
                    alert('Item added to cart!');
                } else {
                    alert('Error: ' + (data.error || 'Failed to add item to cart'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding to cart');
            });
        });
    });

    // Remove item from cart
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            // Implement remove functionality here
            console.log('Remove item:', itemId);
            // You would typically make an AJAX call to remove the item
            // Then reload the page or update the cart dynamically
        });
    });
});
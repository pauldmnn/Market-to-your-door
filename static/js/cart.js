// Get CSRF Token from Cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateNavbarCart(grandTotal, cartCount) {
    let grandTotalElement = document.getElementById("nav-grand-total");
    let cartCountElement = document.getElementById("cart-item-count");

    if (grandTotal !== undefined && !isNaN(grandTotal)) {
        grandTotalElement.textContent = `£${grandTotal.toFixed(2)}`;
    } else {
        grandTotalElement.textContent = "£0.00";
    }

    if (cartCount !== undefined) {
        cartCountElement.textContent = cartCount;
    } else {
        cartCountElement.textContent = "0";
    }
}

// Function to Update Cart
function updateCart(slug, quantity) {
    fetch("/cart/update/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ slug: slug, quantity: quantity }),
    })
    .then((response) => response.json())
    .then((data) => {
        // Update Quantity Field
        if (data.success) {
            let quantityInput = document.querySelector(`#quantity-${slug}`);
            if (quantityInput) {
                quantityInput.value = data.new_quantity;
            }

            // Update Item Total Price
            let totalElement = document.querySelector(`#total-${slug}`);
            if (totalElement) {
                totalElement.textContent = `£${data.total_price.toFixed(2)}`;
            }

            let grandTotalElement = document.getElementById("cart-grand-total");
            if (grandTotalElement) {
                grandTotalElement.textContent = `£${data.grand_total.toFixed(2)}`;
            }

            updateNavbarCart(data.grand_total, data.cart_count);

            if (data.new_quantity == 0) {
                let itemRow = document.getElementById(`cart-item-${slug}`);
                if (itemRow) {
                    itemRow.remove();
                }
            }
            if (data.cart_empty) {
                document.getElementById("cart-container").innerHTML = `
                    <div class="text-center mt-5">
                        <h4>Your cart is empty</h4>
                        <a href="/products/" class="btn btn-primary mt-3">Shop Now</a>
                    </div>`;
            }
        } else {
            alert(data.error);
        }
    })
    .catch((error) => console.error("Error updating cart:", error));
}

function removeFromCart(slug) {
    fetch("/cart/update/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ slug: slug, quantity: 0 }),  // ✅ Sends quantity=0 to remove
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.success) {
            // Remove item row from cart
            let itemRow = document.getElementById(`cart-item-${slug}`);
            if (itemRow) {
                itemRow.remove();
            }

            // Update Navbar Grand Total & Cart Count
            updateNavbarCart(data.grand_total, data.cart_count);

            // Show Empty Cart Message if Needed
            if (data.cart_empty) {
                document.getElementById("cart-container").innerHTML = `
                    <div class="text-center mt-5">
                        <h4>Your cart is empty</h4>
                        <a href="/products/" class="btn btn-primary mt-3">Shop Now</a>
                    </div>`;
            }
        } else {
            alert(data.error);  // ✅ Show error if any
        }
    })
    .catch((error) => console.error("Error removing item:", error));
}

// Event Listeners for Add, Remove, and Update Buttons
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".quantity-btn").forEach((button) => {
        button.addEventListener("click", function () {
            let slug = this.dataset.slug;
            let action = this.dataset.action;
            let quantityInput = document.querySelector(`#quantity-${slug}`);
            let currentQuantity = parseFloat(quantityInput.value);

            if (action === "increase") {
                updateCart(slug, currentQuantity + 1);
            } else if (action === "decrease" && currentQuantity > 1) {
                updateCart(slug, currentQuantity - 1);
            }
        });
    });

    // Update Quantity Manually When User Changes Input Field
document.querySelectorAll(".quantity-input").forEach((input) => {
    input.addEventListener("change", function () {
        let slug = this.dataset.slug;
        let newQuantity = parseFloat(this.value);
        if (newQuantity > 0) {
            updateCart(slug, newQuantity);
        } else {
            updateCart(slug, 0); 
            }
        });
    });
});

    // Remove Item from Cart
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".remove-item").forEach((button) => {
        button.addEventListener("click", function () {
            let slug = this.dataset.slug;
            removeFromCart(slug);
        });
    });
});

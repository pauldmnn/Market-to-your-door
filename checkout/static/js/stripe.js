document.addEventListener("DOMContentLoaded", function () {
    // Ensure that global variables STRIPE_PUBLIC_KEY and CLIENT_SECRET are available
    if (!window.STRIPE_PUBLIC_KEY) {
        console.error("Stripe public key is missing.");
        return;
    }
    if (!window.CLIENT_SECRET) {
        console.error("Stripe client secret is missing.");
        return;
    }

    // Initialize Stripe with the public key
    const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
    const elements = stripe.elements();

    // Custom styling for the card element
    const style = {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSize: '16px',
            '::placeholder': { color: '#aab7c4' },
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545',
        },
    };

    // Create and mount the card element
    const card = elements.create('card', { style: style });
    const cardContainer = document.getElementById('card-element');
    if (!cardContainer) {
        console.error("Card element container (#card-element) not found.");
        return;
    }
    card.mount('#card-element');

    // Handle real-time validation errors from the card element
    card.addEventListener('change', function (event) {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            errorDiv.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-circle"></i> ${event.error.message}</span>`;
        } else {
            errorDiv.textContent = '';
        }
    });

    // Handle form submission
    const form = document.getElementById('payment-form');
    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const submitButton = document.getElementById('submit-button');
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";

        const nameField = document.getElementById("name_on_card");
        if (!nameField) {
            console.error("Name on card field is missing.");
            submitButton.disabled = false;
            submitButton.textContent = "Pay Now";
            return;
        }
        const cardholderName = nameField.value.trim();

        // Confirm the card payment using the PaymentIntent's client secret
        const { error, paymentIntent } = await stripe.confirmCardPayment(CLIENT_SECRET, {
            payment_method: {
                card: card,
                billing_details: { name: cardholderName },
            },
        });

        if (error) {
            document.getElementById("card-errors").innerHTML = `<span class="text-danger">${error.message}</span>`;
            submitButton.disabled = false;
            submitButton.textContent = "Pay Now";
        } else if (paymentIntent && paymentIntent.status === 'succeeded') {
            console.log("Payment succeeded:", paymentIntent);
            // Redirect to order success page using the global ORDER_ID
            if (window.ORDER_ID) {
                window.location.href = "/checkout/order-success/" + window.ORDER_ID + "/";
            } else {
                // Fallback redirection if ORDER_ID is not defined
                window.location.href = "/checkout/success/";
            }
        } else {
            submitButton.disabled = false;
            submitButton.textContent = "Pay Now";
        }
    });
});
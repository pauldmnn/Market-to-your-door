function initStripeElements(clientSecret) {
    // Use the already set global STRIPE_PUBLIC_KEY
    if (!window.STRIPE_PUBLIC_KEY) {
        console.error("Stripe public key is missing.");
        return;
    }
    if (!clientSecret) {
        console.error("Stripe client secret is missing.");
        return;
    }

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

    // Handle real-time validation errors
    card.addEventListener('change', function (event) {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            errorDiv.innerHTML = `<span class="text-danger">${event.error.message}</span>`;
        } else {
            errorDiv.textContent = '';
        }
    });

    // Handle payment form submission
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

        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
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
            if (window.ORDER_ID) {
                window.location.href = "/checkout/order-success/" + window.ORDER_ID + "/";
            } else {
                window.location.href = "/checkout/success/";
            }
        } else {
            submitButton.disabled = false;
            submitButton.textContent = "Pay Now";
        }
    });
}

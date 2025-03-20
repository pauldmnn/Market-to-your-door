document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("checkout-form");
    const submitButton = document.getElementById("submit-button");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";

        // Collect form data
        const formData = new FormData(form);
        
        try {
            const response = await fetch("/checkout/checkout/", {
                method: "POST",
                body: formData
            });
            const data = await response.json();

            if (!data.client_secret) {
                console.error("Failed to retrieve client_secret.");
                submitButton.disabled = false;
                submitButton.textContent = "Place Order";
                return;
            }

            window.CLIENT_SECRET = data.client_secret;
            window.ORDER_ID = data.order_id;

            // Initialize Stripe Elements
            const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
            const elements = stripe.elements();
            const card = elements.create("card");
            card.mount("#card-element");

            // Confirm Payment
            const { error, paymentIntent } = await stripe.confirmCardPayment(window.CLIENT_SECRET, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: document.getElementById("name_on_card").value.trim(),
                    },
                },
            });

            if (error) {
                console.error("Payment error:", error.message);
                document.getElementById("card-errors").textContent = error.message;
                submitButton.disabled = false;
                submitButton.textContent = "Place Order";
            } else if (paymentIntent.status === "succeeded") {
                console.log("Payment succeeded!");
                window.location.href = `/checkout/order-success/${window.ORDER_ID}/`;
            }
        } catch (error) {
            console.error("Error submitting checkout:", error);
            submitButton.disabled = false;
            submitButton.textContent = "Place Order";
        }
    });
});

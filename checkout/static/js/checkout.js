document.addEventListener("DOMContentLoaded", function () {
    const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
    const elements = stripe.elements();

    const card = elements.create("card");
    card.mount("#card-element");

    const form = document.getElementById("checkout-form");
    const submitButton = document.getElementById("submit-button");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";

        const formData = new FormData(form);
        const response = await fetch("/checkout/checkout/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!data.client_secret) {
            console.error("Failed to retrieve client_secret");
            submitButton.disabled = false;
            submitButton.textContent = "Place Order";
            return;
        }

        const result = await stripe.confirmCardPayment(data.client_secret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: document.getElementById("name_on_card").value
                }
            }
        });

        if (result.error) {
            document.getElementById("card-errors").textContent = result.error.message;
            submitButton.disabled = false;
            submitButton.textContent = "Place Order";
        } else {
            if (result.paymentIntent.status === "succeeded") {
                window.location.href = `/checkout/order-success/${data.order_id}/`;
            }
        }
    });
});

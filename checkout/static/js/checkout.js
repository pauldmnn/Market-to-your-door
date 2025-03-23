document.addEventListener("DOMContentLoaded", function () {
    const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
    const elements = stripe.elements();

    const card = elements.create("card", {
        style: {
            base: {
                color: '#32325d',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '16px',
                '::placeholder': { color: '#aab7c4' }
            },
            invalid: {
                color: '#dc3545',
                iconColor: '#dc3545'
            }
        }
    });
    card.mount("#card-element");

    const form = document.getElementById("checkout-form");
    const submitButton = document.getElementById("submit-button");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";

        const formData = new FormData(form);
        let response;
        let data;

        try {
            response = await fetch("/checkout/checkout/", {
                method: "POST",
                body: formData
            });
            data = await response.json();
        } catch (err) {
            console.error("Error creating PaymentIntent:", err);
            submitButton.disabled = false;
            submitButton.textContent = "Place Order";
            return;
        }

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
                    name: document.getElementById("name_on_card").value.trim(),
                    phone: document.getElementById("phone")?.value.trim(),
                    address: {
                        line1: document.getElementById("address_line1")?.value.trim(),
                        line2: document.getElementById("address_line2")?.value.trim(),
                        city: document.getElementById("city")?.value.trim(),
                        state: document.getElementById("county")?.value.trim(),
                        postal_code: document.getElementById("postal_code")?.value.trim(),
                        country: document.getElementById("country")?.value.trim()
                    }
                }
            }
        });

        if (result.error) {
            document.getElementById("card-errors").textContent = result.error.message;
            submitButton.disabled = false;
            submitButton.textContent = "Place Order";
        } else if (result.paymentIntent.status === "succeeded") {
            window.location.href = `/checkout/order-success/${data.order_id}/`;
        }
    });
});

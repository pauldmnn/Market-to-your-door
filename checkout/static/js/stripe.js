document.addEventListener("DOMContentLoaded", function () {
    const stripe = Stripe(document.getElementById("id_stripe_public_key").textContent);
    const clientSecret = document.getElementById("id_client_secret").textContent;

    if (!clientSecret) {
        console.error("Error: Client secret not found.");
        return;
    }

    const elements = stripe.elements();
    const cardElement = elements.create("card", { hidePostalCode: true });
    cardElement.mount("#card-element");

    // Handle form submission
    const form = document.getElementById("payment-form");
    const submitButton = document.getElementById("submit-button");
    const errorMessage = document.getElementById("error-message");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";

        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: cardElement,
                billing_details: {
                    name: document.querySelector("input[name='full_name']").value,
                    email: document.querySelector("input[name='email']").value,
                    address: {
                        line1: document.querySelector("input[name='address']").value,
                        city: document.querySelector("input[name='city']").value,
                        postal_code: document.querySelector("input[name='postal_code']").value,
                        country: document.querySelector("input[name='country']").value,
                    },
                },
            },
        });

        if (error) {
            errorMessage.textContent = error.message;
            submitButton.disabled = false;
            submitButton.textContent = "Pay Now";
        } else {
            window.location.href = "/checkout/success/";
        }
    });
});

import stripe

def create_payment_intent():
    stripe.api_key = 'your_secret_key'

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=1000,  # Amount in cents
            currency='usd',
            payment_method_types=['card'],
            description='Payment for product/service'
        )
        # Send the payment_intent.id to the client
        return payment_intent
    except stripe.error.StripeError as e:
        # Handle error
        print("An error occurred:", e)

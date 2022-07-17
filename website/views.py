from flask import Blueprint, render_template, request, redirect
import stripe

views = Blueprint('views', __name__)
stripe.api_key = 'sk_test_51LLwkYKKfRH6nq6FYChFWFAS1AtNd1FcwNEF8gDFoZeCLUHmU1QnPu3MeAq58cKgPPs1xNBRRJd0Gg1nhhbl5URs00lfFe36AX'
YOUR_DOMAIN = 'http://127.0.0.1:5000'

# This function will run whenever we go to the route defined above
@views.route('/')
def home():
    return render_template("home.html")

@views.route('/compra.html')
def compra():
    return render_template("compra.html")

@views.route('/asientos.html', methods=["GET"])
def asientos():
    if request.method == "GET":
        qty_tickets = request.args.get('qty tickets')
        qty_adulto = request.args.get('qty adulto')
        qty_senior = request.args.get('qty senior')
        qty_child = request.args.get('qty child')
        total_price = request.args.get('total-price')
        return render_template("asientos.html", qty_tickets=qty_tickets, qty_adulto=qty_adulto, qty_senior=qty_senior, qty_child=qty_child, total_price=total_price)


@views.route('/create-checkout-session', methods=["POST"])
def checkout():
    if request.method == 'POST':
        qty_adulto = request.form.get('qty adulto')
        qty_senior = request.form.get('qty senior')
        qty_child = request.form.get('qty child')
        
        arrQty = [qty_adulto, qty_senior, qty_child]
        arrPrice = ['price_1LMDfqKKfRH6nq6FBId7Uyfl', 'price_1LMDgDKKfRH6nq6FHgDxUCUc', 'price_1LMDgXKKfRH6nq6FQsSOydfu']
        line_items = []

        for i in range(3):
            if(arrQty[i] != '0'):
                line_items.append({'price': arrPrice[i], 'quantity': arrQty[i]})

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                success_url= YOUR_DOMAIN + '/success.html',
                cancel_url= YOUR_DOMAIN + '/cancel.html',
            )
        except Exception as e:
            return str(e)

    return redirect(checkout_session.url, code=303)

@views.route('/error.html')
def error():
    return render_template("error.html")

@views.route('/test.html')
def test():
    return render_template("test.html")

@views.route('/testing.html')
def testing():
    return render_template("testing.html")


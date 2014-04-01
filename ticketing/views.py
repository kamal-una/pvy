# Create your views here.
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.http import StreamingHttpResponse
from ticketing import models
from cart import Cart
from django.contrib.auth.decorators import login_required
from forms import UserForm
from django.contrib.auth import authenticate, login


def buy(request):
    t = get_template('buy.html')
    performance = models.get_performances()
    html = render(request, 'buy.html', {'performances': performance})
    return StreamingHttpResponse(html)


def buy_perf(request, performance):
    this_perf = models.get_performance(performance)
    error = None

    if request.method == 'POST':
        data = request.POST
        available_prices = models.get_prices(this_perf)

        # make a new transaction
        transaction = models.create_transaction(request.user)
        redirect_to_cart = False

        # go through the available prices and see what the user has requested
        for price in available_prices:
            buyer = str(price.buyer_type)
            if buyer in data:
                # for each of these buyer_types lock a seat and add it to the cart
                if int(data[buyer]) < 10:
                    for i in range(int(data[buyer])):
                        seat = this_perf.lock_seat(transaction, price.buyer_type, price.price)
                        if seat:
                            cart = Cart(request)
                            cart.add(seat, price.price, 1)
                            redirect_to_cart = True
                else:
                    error = "Invalid number of seats selected"

        # only redirect to the cart if we have added some seats
        if redirect_to_cart:
            return redirect('cart')

    html = render(request, 'buy_perf.html', {'performance': this_perf,
                                             'seat_count': models.get_seat_count(performance),
                                             'prices': models.get_prices(this_perf),
                                             'error': error})
    return StreamingHttpResponse(html)


def get_cart(request):
    return render(request, 'cart.html', dict(cart=Cart(request)))


def empty_cart(request):
    cart = Cart(request)
    transaction = models.create_transaction(request.user)

    for item in cart:
        item.product.unlock_seat(transaction)
        cart.remove(item.product)
    return render(request, 'cart.html', dict(cart=Cart(request)))


@login_required
def purchase(request):
    return render(request, 'purchase.html', dict(cart=Cart(request)))


def confirm(request):
    # mark the seats as paid and remove from cart
    cart = Cart(request)
    transaction = models.create_transaction(request.user)

    for item in cart:
        item.product.pay_seat(transaction, request.user)
        cart.remove(item.product)
    return render(request, 'confirm.html', dict(cart=Cart(request)))


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            print request.POST['password']
            new_user = authenticate(username=new_user.email, password=request.POST['password'])
            if new_user:
                login(request, new_user)
                return redirect('cart')
        else:
            print "form not valid!"
    else:
        form = UserForm()
    return render(request, "register.html", {
        'form': form,
    })
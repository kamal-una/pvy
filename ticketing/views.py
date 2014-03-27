# Create your views here.
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from django.http import StreamingHttpResponse
from ticketing import models
from cart import Cart


def buy(request):
    t = get_template('buy.html')
    performance = models.getPerformances()
    html = render(request, 'buy.html', {'performances': performance})
    return StreamingHttpResponse(html)


def buy_perf(request, year, performance):
    this_perf = models.getPerformance(year, performance)
    error = None

    if request.method == 'POST':
        data = request.POST
        available_prices = models.getPrices(this_perf)

        # go through the available prices and see what the user has requested
        # make a new transaction
        transaction = models.create_transaction(request.user)

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
                else:
                    error = "Invalid number of seats selected"

    html = render(request, 'buy_perf.html', {'performance': this_perf,
                                             'seat_count': models.getSeatCount(year, performance),
                                             'prices': models.getPrices(this_perf),
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


def purchase(request):
    return render(request, 'purchase.html', dict(cart=Cart(request)))


def confirm(request):
    # mark the seats as paid and remove from cart
    cart = Cart(request)
    transaction = models.create_transaction(request.user)

    for item in cart:
        item.product.pay_seat(transaction)
        cart.remove(item.product)
    return render(request, 'confirm.html', dict(cart=Cart(request)))

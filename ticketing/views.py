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

    if request.method == 'POST':
        data = request.POST
        available_prices = models.getPrices(this_perf)

        # go through the available prices and see what the user has requested
        for price in available_prices:
            buyer = str(price.buyer_type)
            if buyer in data:
                # for each of these buyer_types lock a seat and add it to the cart
                for i in range(int(data[buyer])):
                    seat = this_perf.lock_seat(request.user, price.buyer_type, price.price)
                    if seat:
                        cart = Cart(request)
                        cart.add(seat, price.price, 1)


        #models.Transaction.add_cart(data)

    html = render(request, 'buy_perf.html', {'performance': this_perf,
                                             'seat_count': models.getSeatCount(year, performance),
                                             'prices': models.getPrices(this_perf)})
    return StreamingHttpResponse(html)


def get_cart(request):
    return render(request, 'cart.html', dict(cart=Cart(request)))
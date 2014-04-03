# Create your views here.
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.http import StreamingHttpResponse
from ticketing import models
from cart import Cart
from django.contrib.auth.decorators import login_required
from forms import UserForm
from django.contrib.auth import authenticate, login, logout


def buy(request):
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
    cart = Cart(request)
    total = total_cart(cart)
    return render(request, 'cart.html', dict(cart=Cart(request), total=total))


def empty_cart(request):
    cart = Cart(request)
    transaction = models.create_transaction(request.user)

    for item in cart:
        item.product.unlock_seat(transaction)
        cart.remove(item.product)
    return redirect('cart')


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
            new_user = authenticate(username=new_user.email, password=request.POST['password'])
            if new_user:
                login(request, new_user)
                return redirect('cart')
        else:
            print "form not valid!"
    else:
        form = UserForm()
    return render(request, "register.html", {'form': form})


@login_required
def account(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            new_user = form.save()
    form = UserForm(instance=request.user)
    return render(request, "account.html", {'form': form})


def user_logout(request):
    # empty the cart
    cart = Cart(request)
    transaction = models.create_transaction(request.user)
    for item in cart:
        item.product.unlock_seat(transaction)
        cart.remove(item.product)
    logout(request)
    return redirect('login')


def refund_seat(request, seat):
    this_seat = models.get_seat(seat)
    transaction = models.create_transaction(request.user)
    # in real life, we can't just unlock the seat, we would have to refund the payment etc...
    this_seat.user = None
    this_seat.unlock_seat(transaction)

    # direct back to the report for this seat
    return redirect('report_perf', this_seat.performance)


def total_cart(cart):
    total = 0
    for item in cart:
        total += item.product.price
    return total
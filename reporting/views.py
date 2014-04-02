from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from ticketing import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def report(request):
    performances = models.get_report_performances()
    html = render(request, 'report.html', {'performances': performances})
    return StreamingHttpResponse(html)


def report_perf(request, performance):
    this_perf = models.get_performance(performance)
    seats_list = models.get_seats(this_perf)
    paginator = Paginator(seats_list, 100)

    page = request.GET.get('page')
    try:
        seats = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        seats = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        seats = paginator.page(paginator.num_pages)

    html = render(request, 'report_perf.html', {'performance': this_perf, 'seats': seats})
    return StreamingHttpResponse(html)


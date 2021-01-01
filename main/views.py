from django.http import HttpResponse
from django.shortcuts import render, get_list_or_404

from .models import Request, RequestQueue
from .main import analyze_concurrency


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def publish_request_info(request, request_name):
    RequestQueue(request=request_name).save()
    analyze_concurrency()
    all_requests_list = get_list_or_404(Request)
    context = {'all_requests_list': all_requests_list}
    return render(request, 'main/index.html', context)

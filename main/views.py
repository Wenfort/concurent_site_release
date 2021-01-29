from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_list_or_404, redirect

from .models import Request, RequestQueue

from .forms import NewRequest


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def restricted_results(request):
    if request.user.is_staff:
        all_requests_list = get_list_or_404(Request)
        context = {'all_requests_list': all_requests_list}
        return render(request, 'main/restricted_results.html', context)
    else:
        all_requests_list = get_list_or_404(Request)
        context = {'all_requests_list': all_requests_list}
        return render(request, 'main/non_restricted_results.html', context)

def add_new_requests_to_queue(request):
    if request.method == "POST":
        requests_list = request.POST['requests_list']
        requests_list = requests_list.replace('\r','')
        requests_list = requests_list.split('\n')
        for req in requests_list:
            if Request.objects.filter(request=req):
                pass
            else:
                RequestQueue(request=req).save()
                Request(request=req).save()
        return HttpResponseRedirect('/main/restricted_results')
    else:
        form = NewRequest()
        return render(request, 'main/add_to_queue.html', {'form': form})

def account(request):
    return render(request, 'main/account.html')
from django.http import HttpResponse
from django.shortcuts import render, get_list_or_404

from .models import Request, RequestQueue

from .forms import NewRequest


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def publish_request_info(request):
    # RequestQueue(request=request_name).save()
    all_requests_list = get_list_or_404(Request)
    context = {'all_requests_list': all_requests_list}
    return render(request, 'main/index.html', context)

def add_new_requests_to_queue(request):
    if request.method == "POST":
        form = NewRequest(request.POST)
        requests_list = request.POST['requests_list']
        requests_list = requests_list.replace('\r','')
        requests_list = requests_list.split('\n')
        for req in requests_list:
            RequestQueue(request=req).save()
        form = NewRequest()
        return publish_request_info(request)
    else:
        form = NewRequest()
        return render(request, 'main/add_to_queue.html', {'form': form})

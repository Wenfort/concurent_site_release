from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_list_or_404, redirect

from .models import Request, RequestQueue, UserData, Order

from .forms import NewRequest


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def results(request):
    all_requests_list = get_list_or_404(Request.objects.order_by('site_seo_concurency'))
    user_name = request.user.username
    # user = UserData.objects.get(name=user_name)
    try:
        context = {'all_requests_list': all_requests_list, 'user': user}
    except:
        context = {'all_requests_list': all_requests_list}
    if request.user.is_staff:
        return render(request, 'main/restricted_requests.html', context)
    else:
        return render(request, 'main/non_restricted_requests.html', context)


def add_new_requests_to_queue(request):
    if request.method == "POST":

        user_name = request.user.username
        user = UserData.objects.get(name='airlove')


        requests_list = request.POST['requests_list']
        requests_list = requests_list.replace('\r', '')
        requests_list = requests_list.split('\n')
        for req in requests_list:
            if Request.objects.filter(request=req):
                pass
            else:
                RequestQueue(request=req).save()
                Request(request=req).save()

        # order_id = Order.objects.latest('pk').id + 1
        order_id = 1

        new_requests = Request.objects.filter(request__in=requests_list)
        for new_request in new_requests:
            Order(request_id=new_request.id, user_id=user.id, order_id = order_id).save()

        return HttpResponseRedirect('/main/results')
    else:
        form = NewRequest()
        return render(request, 'main/add_to_queue.html', {'form': form})

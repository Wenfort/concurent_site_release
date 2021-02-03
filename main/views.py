from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_list_or_404, redirect

from .models import Request, RequestQueue, UserData, Order

from .forms import NewRequest


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def get_user_data(request):
    user_name = request.user.username
    user = UserData.objects.get(name=user_name)
    user_id = user.id
    user_balance = user.balance

    all_user_order_rows = Order.objects.filter(user_id=user_id)
    unique_user_order_rows = all_user_order_rows.distinct('order_id')

    ordered_keywords_amount = len(all_user_order_rows)
    orders_amount = len(unique_user_order_rows)

    output = {'Объект пользователя': user,
              'Баланс': user_balance,
              'Количество заказов': orders_amount,
              'Количество заказанных ключей': ordered_keywords_amount}

    return output


def results(request):
    all_requests_list = get_list_or_404(Request.objects.order_by('site_seo_concurency'))

    user_data = get_user_data(request)

    try:
        context = {'all_requests_list': all_requests_list,
                   'orders': user_data['Количество заказов'],
                   'keywords_ordered': user_data['Количество заказанных ключей'],
                   'balance': user_data['Баланс']}
    except:
        context = {'all_requests_list': all_requests_list}
    if request.user.is_staff:
        return render(request, 'main/restricted_requests.html', context)
    else:
        return render(request, 'main/non_restricted_requests.html', context)


def add_new_requests_to_queue(request):
    if request.method == "POST":

        user_data = get_user_data(request)

        requests_list = request.POST['requests_list']
        requests_list = requests_list.replace('\r', '')
        requests_list = requests_list.split('\n')
        for req in requests_list:
            if Request.objects.filter(request=req):
                pass
            else:
                RequestQueue(request=req).save()
                Request(request=req).save()

        order_id = Order.objects.latest('pk').id + 1

        new_requests = Request.objects.filter(request__in=requests_list)
        new_requests_amount = len(new_requests)
        for new_request in new_requests:
            Order(request_id=new_request.id,
                  user_id=user_data['Объект пользователя'].id,
                  order_id=order_id
                  ).save()

        UserData(id=user_data['Объект пользователя'].id,
                 balance=user_data['Объект пользователя'].balance - new_requests_amount,
                 name=user_data['Объект пользователя'].name,
                 ).save()

        return HttpResponseRedirect('/main/results')
    else:
        form = NewRequest()
        return render(request, 'main/add_to_queue.html', {'form': form})


def get_orders_page(request):
    context = {'orders': unique_user_order_rows, 'ordered_keywords': ordered_keywords_amount, 'user': user_data,
               'orders_amount': orders_amount}
    return render(request, 'main/orders.html', context)

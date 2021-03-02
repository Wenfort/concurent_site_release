import time
from postgres_mode import establish_connection
from custom_send_email import send_order_ready_mail

while True:
    connection = establish_connection()
    cursor = connection.cursor()
    sql_request = 'SELECT order_id, user_id, user_order_id FROM concurent_site.main_orderstatus WHERE status = 0'
    cursor.execute(sql_request)
    pending_orders = [(item[0], item[1], item[2]) for item in cursor.fetchall()]



    for pending_order in pending_orders:
        order_id = pending_order[0]
        user_id = pending_order[1]
        user_order_id = pending_order[2]
        sql_request = f'SELECT request_id FROM concurent_site.main_order WHERE order_id = {order_id}'
        cursor.execute(sql_request)
        order_requests = [str(item[0]) for item in cursor.fetchall()]
        order_requests = ','.join(order_requests)

        sql_request = f'SELECT status FROM concurent_site.main_request WHERE request_id IN ({order_requests})'
        cursor.execute(sql_request)
        order_requests = [str(item[0]) for item in cursor.fetchall()]

        total_requests = len(order_requests)
        complete_requests = 0

        for order_request in order_requests:
            if order_request == 'ready':
                complete_requests += 1

        complete_requests_percent = int(complete_requests / total_requests * 100)

        if complete_requests_percent == 100:
            sql_request = f"UPDATE concurent_site.main_orderstatus SET status = 1, progress = {complete_requests_percent} WHERE order_id = {order_id};"
            email_request = f'SELECT email FROM concurent_site.auth_user WHERE id = {user_id}'
            cursor.execute(email_request)
            email = cursor.fetchone()[0]
            send_order_ready_mail(email, user_order_id)
        else:
            sql_request = f'UPDATE concurent_site.main_orderstatus SET progress = {complete_requests_percent} WHERE order_id = {order_id};'

        cursor.execute(sql_request)
    connection.commit()

    connection.close()
    time.sleep(15)
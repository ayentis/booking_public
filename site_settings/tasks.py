import logging

from django.apps import apps
from site_settings.celery_app import app
from site_settings.tools import ApartmentBookingStatus

logger = logging.getLogger('django')


@app.task
def cancel_not_payed_on_hold_order(order_id):
    logger.error(f"start task")
    try:
        Order = apps.get_model(app_label='booking', model_name='Order')
        order = Order.objects.get(pk=order_id)
        if order.status == ApartmentBookingStatus.ON_HOLD:
            order.status = ApartmentBookingStatus.CANCELED
            order.save()
    except BaseException as e:
        logger.error(f"Can't cancel order {order_id}: {e}")


@app.task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          request.id, exc, traceback))
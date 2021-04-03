from django.db import models
from taxi.models import User, Driver, Card

# Create your models here.
STATUS = (
    (0, "Inactive"),
    (1, "Active"),
)


class ClassBase(models.Model):
    is_active = models.IntegerField(choices=STATUS, default=1)
    insert_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Book(ClassBase):
    BOOK_TYPE = (
        (1, 'Truck'),
        (2, 'Bike')
    )
    SHIPMENT_TYPE = (
        (1, 'Domestic'),
        (2, 'International')
    )
    MATERIAL_TYPE = (
        (1, 'Person'),
        (2, 'Package')
    )
    CHOICE = (
        (1, "Card"),
        (2, "COD"),
        (3, "Wallet")
    )
    BOOK_STATUS = (
        (1, 'Pending'),
        (2, 'Pickup'),
        (3, 'Complete'),
        (0, 'Canceled'),
    )
    booking_type = models.IntegerField(choices=BOOK_TYPE, default=1)
    pick_up_lat = models.CharField(max_length=16)  # lattitude of Pick Up
    pick_up_lon = models.CharField(max_length=16)  # longitude of Pick Up
    drop_lat = models.CharField(max_length=16)  # lattitude of Drop
    drop_lon = models.CharField(max_length=16)  # longitude of Drop
    capacity = models.IntegerField(null=True)  # if user user choose book type truck or will null
    shipment_type = models.IntegerField(choices=SHIPMENT_TYPE, default=1,
                                        null=True)  # if user choose book type truck or will null

    document = models.CharField(max_length=16, null=True)  # if user choose book type truck or will null
    material_type = models.IntegerField(choices=MATERIAL_TYPE,
                                        null=True)  # if user choose book type bike or will null

    payment_type = models.IntegerField(choices=CHOICE, default=2, null=True)
    card_pay_id = models.ForeignKey(Card, on_delete=models.SET_NULL,
                                    null=True)  # if user choose payment type card or will null

    user = models.ForeignKey(User, related_name='customer', on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(Driver, related_name='driver', on_delete=models.SET_NULL, null=True)
    duration = models.CharField(max_length=8, default=0)
    distance = models.IntegerField(null=True)
    status = models.IntegerField(choices=BOOK_STATUS, default=1)
    total_amount = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        db_table = 'tbl_book'

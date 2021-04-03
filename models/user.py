from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
STATUS = (
        (0, "Inactive"),
        (1, "Active"),
    )


class Country(models.Model):
    iso = models.CharField(max_length=2)
    name = models.CharField(max_length=128)
    full_name = models.CharField(max_length=128)
    iso3 = models.CharField(max_length=3, null=True)
    numcode = models.CharField(max_length=8, null=True)
    phonecode = models.CharField(max_length=8)
    update_date = models.DateTimeField(auto_now=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tbl_country"

    def __str__(self):
        return f"{str(self.pk)}:\t{str(self.name)+' '+str(self.numcode)+' '+str(self.phonecode)}"


class User(AbstractUser):
    user_types = (
        (1, "simple"),
        (2, "driver")
    )
    OTP_VERIFIED = (
        (0, "unverified"),
        (1, "verified")
    )

    username = None
    first_name = None
    last_name = None

    fullname = models.CharField(max_length=128)
    email = models.EmailField(max_length=128, unique=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=12, unique=True)
    profile_image = models.ImageField(upload_to='profile_image/', blank=True, default='profile_image/default.png')
    wallet = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    user_type = models.IntegerField(default=1, choices=user_types)
    otp = models.IntegerField(default=1234)
    otp_verified = models.IntegerField(choices=OTP_VERIFIED, default=0)
    update_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return f"{str(self.pk)}:\t{str(self.fullname)}"


class ClassBase(models.Model):

    is_active = models.IntegerField(choices=STATUS, default=1)
    insert_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Driver(ClassBase):
    VEHICLE_TYPE = (
        (1, "bike"),
        (2, "truck")
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    licence = models.CharField(max_length=16)
    type_vehicle = models.IntegerField(choices=VEHICLE_TYPE, default=2)
    capacity = models.IntegerField()
    rc_book = models.CharField(max_length=16)
    fittness_certificate = models.CharField(max_length=16)
    insurance = models.CharField(max_length=16)
    rate = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    review = models.IntegerField(default=0)

    class Meta:
        db_table = "tbl_driver"


class Card(ClassBase):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_no = models.CharField(max_length=16)
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=2)
    name = models.CharField(max_length=128)

    class Meta:
        db_table = 'tbl_card'

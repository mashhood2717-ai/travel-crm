from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


SERVICE_CHOICES = [
    ("UMRAH", "Umrah"),
    ("HAJJ", "Hajj"),
    ("VISIT", "Visit Visa"),
    ("FLIGHT_INTL", "International Flight"),
    ("FLIGHT_DOM", "Domestic Flight"),
    ("TOUR", "Tour Package"),
    ("OTHER", "Other"),
]

GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Passenger(TimeStamped):
    full_name = models.CharField(max_length=150, db_index=True)
    father_name = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    date_of_birth = models.DateField(null=True, blank=True)

    cnic = models.CharField("CNIC", max_length=20, blank=True, db_index=True)
    passport_number = models.CharField(max_length=30, blank=True, db_index=True)
    passport_expiry = models.DateField(null=True, blank=True)
    passport_issue_country = models.CharField(max_length=60, blank=True, default="Pakistan")

    visa_number = models.CharField(max_length=60, blank=True)
    visa_expiry = models.DateField(null=True, blank=True)

    mobile = models.CharField(max_length=25, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["passport_number"]),
            models.Index(fields=["cnic"]),
            models.Index(fields=["mobile"]),
        ]

    def __str__(self):
        return f"{self.full_name}" + (f" ({self.passport_number})" if self.passport_number else "")

    def get_absolute_url(self):
        return reverse("passenger_detail", args=[self.pk])

    @property
    def passport_expiring_soon(self):
        if not self.passport_expiry:
            return False
        return self.passport_expiry <= (timezone.now().date() + timedelta(days=180))

    @property
    def visa_expiring_soon(self):
        if not self.visa_expiry:
            return False
        return self.visa_expiry <= (timezone.now().date() + timedelta(days=30))


class Group(TimeStamped):
    name = models.CharField(max_length=150)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default="UMRAH")
    group_head = models.ForeignKey(
        Passenger, on_delete=models.SET_NULL, null=True, blank=True, related_name="led_groups"
    )
    departure_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    destination = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    members = models.ManyToManyField(Passenger, through="GroupMembership", related_name="groups")

    class Meta:
        ordering = ["-departure_date", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"

    def get_absolute_url(self):
        return reverse("group_detail", args=[self.pk])

    @property
    def member_count(self):
        return self.members.count()


class GroupMembership(TimeStamped):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True, default="Member")

    class Meta:
        unique_together = ("group", "passenger")


def passenger_doc_path(instance, filename):
    return f"passengers/{instance.passenger_id}/{filename}"


class Document(TimeStamped):
    DOC_TYPES = [
        ("PASSPORT", "Passport Scan"),
        ("VISA", "Visa Copy"),
        ("TICKET", "E-Ticket"),
        ("CNIC", "CNIC"),
        ("PHOTO", "Photo"),
        ("OTHER", "Other"),
    ]
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, default="PASSPORT")
    file = models.FileField(upload_to=passenger_doc_path)
    description = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.passenger.full_name}"


class Supplier(TimeStamped):
    SUPPLIER_TYPES = [
        ("AIRLINE", "Airline"),
        ("HOTEL", "Hotel"),
        ("VISA", "Visa Provider"),
        ("TRANSPORT", "Transport"),
        ("OTHER", "Other"),
    ]
    name = models.CharField(max_length=150, unique=True)
    supplier_type = models.CharField(max_length=20, choices=SUPPLIER_TYPES, default="OTHER")
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def total_paid(self):
        return self.payments.aggregate(s=models.Sum("amount"))["s"] or Decimal("0")


class Booking(TimeStamped):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]
    reference = models.CharField(max_length=20, unique=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default="UMRAH")
    passenger = models.ForeignKey(Passenger, on_delete=models.PROTECT, related_name="bookings")
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, related_name="bookings")

    package_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    travel_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} - {self.passenger.full_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            super().save(*args, **kwargs)
            self.reference = f"BK-{self.pk:06d}"
            kwargs["force_insert"] = False
            return super().save(update_fields=["reference"])
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("booking_detail", args=[self.pk])

    @property
    def net_total(self):
        return (self.package_cost or Decimal("0")) - (self.discount or Decimal("0"))

    @property
    def total_received(self):
        return self.payments.aggregate(s=models.Sum("amount"))["s"] or Decimal("0")

    @property
    def balance_due(self):
        return self.net_total - self.total_received


class Payment(TimeStamped):
    METHOD_CHOICES = [
        ("CASH", "Cash"),
        ("BANK", "Bank Transfer"),
        ("CARD", "Card"),
        ("CHEQUE", "Cheque"),
        ("OTHER", "Other"),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="CASH")
    received_on = models.DateField(default=timezone.now)
    reference = models.CharField(max_length=80, blank=True)
    note = models.CharField(max_length=200, blank=True)
    received_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-received_on", "-id"]

    def __str__(self):
        return f"{self.amount} on {self.received_on}"


class SupplierPayment(TimeStamped):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="payments")
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, related_name="supplier_payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_on = models.DateField(default=timezone.now)
    method = models.CharField(max_length=20, choices=Payment.METHOD_CHOICES, default="BANK")
    reference = models.CharField(max_length=80, blank=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-paid_on", "-id"]

    def __str__(self):
        return f"{self.supplier.name} - {self.amount}"

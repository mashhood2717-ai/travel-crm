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

PAX_TYPE_CHOICES = [
    ("ADULT", "Adult"),
    ("CHILD", "Child"),
    ("INFANT", "Infant"),
]

MEAL_PLAN_CHOICES = [
    ("RO", "RO"),
    ("BB", "BB"),
    ("HB", "HB"),
    ("FB", "FB"),
    ("AI", "AI"),
]

FLIGHT_DIRECTION_CHOICES = [
    ("OUT", "Departure from Pakistan to KSA"),
    ("IN", "Departure from KSA to Pakistan"),
]

ROOM_TYPE_CHOICES = [
    ("SINGLE", "Single (1 Bed)"),
    ("DOUBLE", "Double (2 Beds)"),
    ("TRIPLE", "Triple (3 Beds)"),
    ("QUAD", "Quad (4 Beds)"),
    ("QUINT", "Quintuple (5 Beds)"),
    ("FAMILY", "Family Suite"),
    ("OTHER", "Other"),
]

ROOM_BASIS_CHOICES = [
    ("SHARING", "Sharing (with other pilgrims)"),
    ("PRIVATE", "Private (own room)"),
]

MEAL_PLAN_CHOICES = [
    ("RO", "Room Only (RO)"),
    ("BB", "Bed & Breakfast (BB)"),
    ("HB", "Half Board (HB)"),
    ("FB", "Full Board (FB)"),
]

PAX_TYPE_CHOICES = [
    ("ADULT", "Adult"),
    ("CHILD", "Child"),
    ("INFANT", "Infant"),
]

FLIGHT_DIRECTION_CHOICES = [
    ("OUT", "Pakistan to KSA"),
    ("IN", "KSA to Pakistan"),
    ("OTHER", "Other"),
]

TRANSPORT_MODE_CHOICES = [
    ("BUS", "Bus (Sharing / Group)"),
    ("PRIVATE", "Private Car"),
    ("VAN", "Van / Coaster"),
    ("GMC", "GMC / SUV"),
    ("TRAIN", "Haramain Train"),
    ("OTHER", "Other"),
]


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, related_name="%(class)s_created", on_delete=models.SET_NULL)
    updated_by = models.ForeignKey('auth.User', null=True, blank=True, related_name="%(class)s_updated", on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

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
            models.Index(fields=["is_active"]),
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
        indexes = [models.Index(fields=["is_active"])]

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

    # Hotel-voucher metadata
    voucher_no = models.CharField(max_length=30, blank=True)
    voucher_date = models.DateField(null=True, blank=True)
    branch = models.CharField(max_length=50, blank=True)
    saudi_company = models.CharField(max_length=200, blank=True)
    package_label = models.CharField(max_length=100, blank=True)
    manual_no = models.CharField(max_length=50, blank=True)
    group_no = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    voucher_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_active"])]

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

    @property
    def effective_voucher_no(self):
        return self.voucher_no or (f"UB-{self.pk:06d}" if self.pk else "")

    @property
    def all_pilgrims(self):
        """Family head + extra pilgrims, in order."""
        items = [{
            "passenger": self.passenger,
            "pax_type": "ADULT",
            "pax_type_display": "Adult",
            "bed": True,
            "visa_number": getattr(self.passenger, "visa_number", "") or "",
            "pnr": "",
            "is_head": True,
        }]
        for ep in self.extra_pax.select_related("passenger").all():
            items.append({
                "passenger": ep.passenger,
                "pax_type": ep.pax_type,
                "pax_type_display": ep.get_pax_type_display(),
                "bed": ep.bed,
                "visa_number": ep.visa_number or (getattr(ep.passenger, "visa_number", "") or ""),
                "pnr": ep.pnr,
                "is_head": False,
            })
        return items

    @property
    def total_pax(self):
        return 1 + self.extra_pax.count()

    @property
    def adults_count(self):
        return 1 + self.extra_pax.filter(pax_type="ADULT").count()

    @property
    def children_count(self):
        return self.extra_pax.filter(pax_type="CHILD").count()

    @property
    def infants_count(self):
        return self.extra_pax.filter(pax_type="INFANT").count()

    @property
    def total_beds(self):
        beds = 1  # head
        beds += self.extra_pax.filter(bed=True).count()
        return beds

    @property
    def total_nights(self):
        return sum(h.nights for h in self.hotels.all())


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


class BookingHotel(TimeStamped):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="hotels")
    hotel = models.ForeignKey("Hotel", on_delete=models.PROTECT, related_name="booking_stays")
    confirm_no = models.CharField(max_length=80, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default="DOUBLE")
    room_basis = models.CharField(max_length=10, choices=ROOM_BASIS_CHOICES, default="SHARING")
    rooms_count = models.PositiveSmallIntegerField(default=1, help_text="How many rooms of this type")
    occupants = models.PositiveSmallIntegerField(default=2, help_text="People per room")
    extra_bed = models.BooleanField(default=False)
    room_notes = models.CharField(max_length=200, blank=True, help_text="e.g. mother+daughter, no smoking, view")
    meal_plan = models.CharField(max_length=4, choices=MEAL_PLAN_CHOICES, default="RO")
    check_in = models.DateField()
    check_out = models.DateField()

    class Meta:
        ordering = ["check_in", "id"]

    def __str__(self):
        return f"{self.hotel.name} ({self.hotel.city})"

    @property
    def hotel_name(self):
        return self.hotel.name

    @property
    def city(self):
        return self.hotel.city

    @property
    def room_label(self):
        """Pretty label like '2x Triple Sharing' for vouchers/lists."""
        rt = self.get_room_type_display().split(" (")[0]
        basis = "Sharing" if self.room_basis == "SHARING" else "Private"
        prefix = f"{self.rooms_count}x " if self.rooms_count > 1 else ""
        suffix = " +Extra Bed" if self.extra_bed else ""
        return f"{prefix}{rt} {basis}{suffix}"

    @property
    def total_beds(self):
        beds_per_type = {"SINGLE": 1, "DOUBLE": 2, "TRIPLE": 3, "QUAD": 4, "QUINT": 5}
        return beds_per_type.get(self.room_type, self.occupants) * self.rooms_count + (
            self.rooms_count if self.extra_bed else 0
        )

    @property
    def nights(self):
        if self.check_in and self.check_out:
            return max((self.check_out - self.check_in).days, 0)
        return 0


class BookingFlight(TimeStamped):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="flights")
    airline = models.ForeignKey("Airline", null=True, blank=True, on_delete=models.SET_NULL, related_name="booking_flights")
    direction = models.CharField(max_length=10, choices=FLIGHT_DIRECTION_CHOICES, default="OUT")
    flight_no = models.CharField(max_length=20)
    sector = models.CharField(max_length=50, blank=True)
    departure = models.DateTimeField(null=True, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["direction", "departure", "id"]

    def __str__(self):
        return f"{self.flight_no} {self.sector}"

    @property
    def airline_name(self):
        return self.airline.name if self.airline else ""


class BookingTransport(TimeStamped):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="transports")
    name = models.CharField(max_length=120, help_text="Route or service name (e.g. JED-MAK-MED-JED)")
    transport_mode = models.CharField(max_length=10, choices=TRANSPORT_MODE_CHOICES, default="BUS")
    transport_type = models.CharField(max_length=120, blank=True, help_text="Optional details (e.g. AC Coaster, Toyota Hiace)")
    brn = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} - {self.get_transport_mode_display()}"

    @property
    def mode_label(self):
        return self.get_transport_mode_display()


class BookingPassenger(TimeStamped):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="extra_pax")
    passenger = models.ForeignKey(Passenger, on_delete=models.PROTECT)
    pax_type = models.CharField(max_length=10, choices=PAX_TYPE_CHOICES, default="ADULT")
    bed = models.BooleanField(default=True)
    visa_number = models.CharField(max_length=80, blank=True)
    pnr = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["id"]
        unique_together = [("booking", "passenger")]

    def __str__(self):
        return f"{self.passenger.full_name} ({self.get_pax_type_display()})"


class Hotel(TimeStamped):
    name = models.CharField(max_length=200, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    default_meal_plan = models.CharField(max_length=4, choices=MEAL_PLAN_CHOICES, default="RO")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["city", "name"]
        unique_together = [("name", "city")]
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self):
        return f"{self.name} — {self.city}"

    def get_absolute_url(self):
        return reverse("hotel_list")


class Airline(TimeStamped):
    name = models.CharField(max_length=120, unique=True, db_index=True)
    code = models.CharField(max_length=10, blank=True, help_text="IATA code, e.g. SV, PK, EK")
    country = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self):
        return self.name if not self.code else f"{self.name} ({self.code})"

    def get_absolute_url(self):
        return reverse("airline_list")

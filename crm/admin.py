from django.contrib import admin
from .models import (
    Passenger, Group, GroupMembership, Document, Booking, Payment,
    Supplier, SupplierPayment,
    BookingHotel, BookingFlight, BookingTransport, BookingPassenger, Hotel, Airline,
)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "passport_number", "cnic", "mobile", "passport_expiry", "visa_expiry", "is_active")
    search_fields = ("full_name", "passport_number", "cnic", "mobile", "email")
    list_filter = ("is_active", "gender", "passport_issue_country")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


class MembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "service_type", "departure_date", "destination", "member_count")
    list_filter = ("service_type",)
    search_fields = ("name", "destination")
    inlines = [MembershipInline]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("passenger", "doc_type", "created_at")
    list_filter = ("doc_type",)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class BookingHotelInline(admin.TabularInline):
    model = BookingHotel
    extra = 0


class BookingFlightInline(admin.TabularInline):
    model = BookingFlight
    extra = 0


class BookingTransportInline(admin.TabularInline):
    model = BookingTransport
    extra = 0


class BookingPassengerInline(admin.TabularInline):
    model = BookingPassenger
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "passenger", "service_type", "package_cost", "status", "travel_date", "is_active")
    list_filter = ("is_active", "service_type", "status")
    search_fields = ("reference", "passenger__full_name", "passenger__passport_number")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    inlines = [BookingPassengerInline, BookingHotelInline, BookingFlightInline, BookingTransportInline, PaymentInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier_type", "phone", "email")
    list_filter = ("supplier_type",)
    search_fields = ("name", "contact_person", "phone")


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ("supplier", "amount", "paid_on", "method", "booking")
    list_filter = ("method", "supplier")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "default_meal_plan", "is_active")
    list_filter = ("is_active", "city", "default_meal_plan")
    search_fields = ("name", "city")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "country", "phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "country")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

from django import forms
from .models import (
    Passenger, Group, Document, Booking, Payment, Supplier, SupplierPayment, GroupMembership,
    BookingHotel, BookingFlight, BookingTransport, BookingPassenger, Hotel, Airline,
)


class DateInput(forms.DateInput):
    input_type = "date"


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = [
            "full_name", "father_name", "gender", "date_of_birth",
            "cnic", "passport_number", "passport_expiry", "passport_issue_country",
            "visa_number", "visa_expiry",
            "mobile", "email", "address", "notes",
        ]
        widgets = {
            "date_of_birth": DateInput(),
            "passport_expiry": DateInput(),
            "visa_expiry": DateInput(),
            "address": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "service_type", "group_head", "departure_date", "return_date", "destination", "notes"]
        widgets = {
            "departure_date": DateInput(),
            "return_date": DateInput(),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class GroupMembershipForm(forms.ModelForm):
    class Meta:
        model = GroupMembership
        fields = ["passenger", "role"]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_type", "file", "description"]


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "service_type", "passenger", "group",
            "package_cost", "discount", "travel_date", "status", "description",
            "voucher_no", "voucher_date", "branch", "saudi_company",
            "package_label", "manual_no", "group_no", "whatsapp", "voucher_note",
        ]
        widgets = {
            "travel_date": DateInput(),
            "voucher_date": DateInput(),
            "description": forms.Textarea(attrs={"rows": 2}),
            "voucher_note": forms.Textarea(attrs={"rows": 2}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "method", "received_on", "reference", "note"]
        widgets = {"received_on": DateInput()}


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "supplier_type", "contact_person", "phone", "email", "address", "notes"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierPayment
        fields = ["supplier", "booking", "amount", "method", "paid_on", "reference", "note"]
        widgets = {"paid_on": DateInput()}


class BookingHotelForm(forms.ModelForm):
    class Meta:
        model = BookingHotel
        fields = [
            "hotel", "confirm_no",
            "room_type", "room_basis", "rooms_count", "occupants",
            "extra_bed", "room_notes",
            "meal_plan", "check_in", "check_out",
        ]
        widgets = {
            "check_in": DateInput(),
            "check_out": DateInput(),
            "confirm_no": forms.TextInput(attrs={"placeholder": "Confirmation No (optional)"}),
            "room_notes": forms.TextInput(attrs={"placeholder": "e.g. mother+daughter, ground floor"}),
            "rooms_count": forms.NumberInput(attrs={"min": 1}),
            "occupants": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hotel"].queryset = Hotel.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        ci, co = cleaned.get("check_in"), cleaned.get("check_out")
        if ci and co and co < ci:
            raise forms.ValidationError("Check-out date must be on or after check-in date.")
        return cleaned


class BookingFlightForm(forms.ModelForm):
    class Meta:
        model = BookingFlight
        fields = ["airline", "direction", "flight_no", "sector", "departure", "arrival"]
        widgets = {
            "departure": DateTimeInput(),
            "arrival": DateTimeInput(),
            "flight_no": forms.TextInput(attrs={"placeholder": "Flight # (e.g. SV-801)"}),
            "sector": forms.TextInput(attrs={"placeholder": "Sector (e.g. MUX-JED)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["airline"].queryset = Airline.objects.filter(is_active=True)


class BookingTransportForm(forms.ModelForm):
    class Meta:
        model = BookingTransport
        fields = ["name", "transport_mode", "transport_type", "brn"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Route name (e.g. JED-MAK-MED-JED)"}),
            "transport_type": forms.TextInput(attrs={"placeholder": "Details (e.g. AC Coaster, Toyota Hiace)"}),
            "brn": forms.TextInput(attrs={"placeholder": "BRN (optional)"}),
        }


class BookingPassengerForm(forms.ModelForm):
    class Meta:
        model = BookingPassenger
        fields = ["passenger", "pax_type", "bed", "visa_number", "pnr"]
        widgets = {
            "visa_number": forms.TextInput(attrs={"placeholder": "Visa Number"}),
            "pnr": forms.TextInput(attrs={"placeholder": "PNR (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["passenger"].queryset = Passenger.objects.filter(is_active=True)


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ["name", "city", "address", "phone", "default_meal_plan", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Hotel name (e.g. Mila 1 Hotel)"}),
            "city": forms.TextInput(attrs={"placeholder": "City (e.g. Makkah)"}),
            "address": forms.TextInput(attrs={"placeholder": "Address"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class AirlineForm(forms.ModelForm):
    class Meta:
        model = Airline
        fields = ["name", "code", "country", "phone", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Airline name (e.g. Saudia, PIA, Emirates)"}),
            "code": forms.TextInput(attrs={"placeholder": "IATA code (e.g. SV, PK, EK)"}),
            "country": forms.TextInput(attrs={"placeholder": "Country"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

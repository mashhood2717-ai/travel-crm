from django import forms
from .models import Passenger, Group, Document, Booking, Payment, Supplier, SupplierPayment, GroupMembership


class DateInput(forms.DateInput):
    input_type = "date"


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
        fields = ["service_type", "passenger", "group", "package_cost", "discount", "travel_date", "status", "description"]
        widgets = {
            "travel_date": DateInput(),
            "description": forms.Textarea(attrs={"rows": 2}),
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

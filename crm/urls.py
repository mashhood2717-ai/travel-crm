from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Passengers
    path("passengers/", views.passenger_list, name="passenger_list"),
    path("passengers/new/", views.passenger_create, name="passenger_create"),
    path("passengers/<int:pk>/", views.passenger_detail, name="passenger_detail"),
    path("passengers/<int:pk>/edit/", views.passenger_edit, name="passenger_edit"),
    path("passengers/<int:pk>/delete/", views.passenger_delete, name="passenger_delete"),
    path("passengers/<int:pk>/upload/", views.document_upload, name="document_upload"),
    path("documents/<int:pk>/delete/", views.document_delete, name="document_delete"),
    path("passengers/export/excel/", views.export_passengers_excel, name="export_passengers_excel"),
    path("passengers/export/pdf/", views.export_passengers_pdf, name="export_passengers_pdf"),

    # Groups
    path("groups/", views.group_list, name="group_list"),
    path("groups/new/", views.group_create, name="group_create"),
    path("groups/<int:pk>/", views.group_detail, name="group_detail"),
    path("groups/<int:pk>/edit/", views.group_edit, name="group_edit"),
    path("groups/<int:pk>/delete/", views.group_delete, name="group_delete"),
    path("groups/<int:pk>/add-member/", views.group_add_member, name="group_add_member"),
    path("groups/<int:pk>/remove-member/<int:passenger_id>/", views.group_remove_member, name="group_remove_member"),

    # Bookings
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/new/", views.booking_create, name="booking_create"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/edit/", views.booking_edit, name="booking_edit"),
    path("bookings/<int:pk>/delete/", views.booking_delete, name="booking_delete"),
    path("bookings/<int:pk>/payment/", views.payment_create, name="payment_create"),
    path("bookings/<int:pk>/invoice/", views.booking_invoice_pdf, name="booking_invoice_pdf"),
    path("bookings/<int:pk>/receipt/<int:payment_id>/", views.payment_receipt_pdf, name="payment_receipt_pdf"),

    # Suppliers
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/new/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/", views.supplier_detail, name="supplier_detail"),
    path("suppliers/<int:pk>/edit/", views.supplier_edit, name="supplier_edit"),
    path("suppliers/<int:pk>/pay/", views.supplier_payment_create, name="supplier_payment_create"),

    # Reports
    path("reports/financial/", views.financial_report, name="financial_report"),
    path("reports/financial/excel/", views.export_financial_excel, name="export_financial_excel"),
]

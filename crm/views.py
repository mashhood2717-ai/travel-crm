from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Passenger, Group, GroupMembership, Document,
    Booking, Payment, Supplier, SupplierPayment, SERVICE_CHOICES,
)
from .forms import (
    PassengerForm, GroupForm, GroupMembershipForm, DocumentForm,
    BookingForm, PaymentForm, SupplierForm, SupplierPaymentForm,
)


# ---------- Dashboard ----------

@login_required
def dashboard(request):
    today = timezone.now().date()
    soon_passport = today + timedelta(days=180)
    soon_visa = today + timedelta(days=30)

    expiring_passports = Passenger.objects.filter(
        passport_expiry__isnull=False, passport_expiry__lte=soon_passport
    ).order_by("passport_expiry")[:10]

    expiring_visas = Passenger.objects.filter(
        visa_expiry__isnull=False, visa_expiry__lte=soon_visa
    ).order_by("visa_expiry")[:10]

    today_bookings = Booking.objects.filter(created_at__date=today).count()
    pending_payments = Booking.objects.exclude(status="CANCELLED")
    total_billed = pending_payments.aggregate(s=Sum("package_cost"))["s"] or Decimal("0")
    total_received = Payment.objects.filter(booking__in=pending_payments).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    outstanding = total_billed - total_received

    upcoming_departures = Group.objects.filter(
        departure_date__isnull=False, departure_date__gte=today
    ).order_by("departure_date")[:5]

    by_service = (
        Booking.objects.values("service_type")
        .annotate(c=Count("id"))
        .order_by("-c")
    )

    ctx = {
        "expiring_passports": expiring_passports,
        "expiring_visas": expiring_visas,
        "today_bookings": today_bookings,
        "total_billed": total_billed,
        "total_received": total_received,
        "outstanding": outstanding,
        "upcoming_departures": upcoming_departures,
        "by_service": by_service,
        "recent_bookings": Booking.objects.select_related("passenger")[:8],
        "passenger_count": Passenger.objects.count(),
        "group_count": Group.objects.count(),
    }
    return render(request, "crm/dashboard.html", ctx)


# ---------- Passengers ----------

@login_required
def passenger_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Passenger.objects.all()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(passport_number__icontains=q)
            | Q(cnic__icontains=q)
            | Q(mobile__icontains=q)
            | Q(email__icontains=q)
        )
    return render(request, "crm/passenger_list.html", {"passengers": qs[:500], "q": q, "total": qs.count()})


@login_required
@permission_required("crm.add_passenger", raise_exception=True)
def passenger_create(request):
    form = PassengerForm(request.POST or None)
    if form.is_valid():
        p = form.save()
        messages.success(request, "Passenger created.")
        return redirect(p.get_absolute_url())
    return render(request, "crm/passenger_form.html", {"form": form, "title": "New Passenger"})


@login_required
def passenger_detail(request, pk):
    p = get_object_or_404(Passenger, pk=pk)
    doc_form = DocumentForm()
    return render(request, "crm/passenger_detail.html", {
        "p": p, "doc_form": doc_form,
        "bookings": p.bookings.all(),
    })


@login_required
@permission_required("crm.change_passenger", raise_exception=True)
def passenger_edit(request, pk):
    p = get_object_or_404(Passenger, pk=pk)
    form = PassengerForm(request.POST or None, instance=p)
    if form.is_valid():
        form.save()
        messages.success(request, "Passenger updated.")
        return redirect(p.get_absolute_url())
    return render(request, "crm/passenger_form.html", {"form": form, "title": "Edit Passenger"})


@login_required
@permission_required("crm.delete_passenger", raise_exception=True)
@require_POST
def passenger_delete(request, pk):
    p = get_object_or_404(Passenger, pk=pk)
    p.delete()
    messages.success(request, "Passenger deleted.")
    return redirect("passenger_list")


@login_required
@permission_required("crm.add_document", raise_exception=True)
@require_POST
def document_upload(request, pk):
    p = get_object_or_404(Passenger, pk=pk)
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.passenger = p
        doc.uploaded_by = request.user
        doc.save()
        messages.success(request, "Document uploaded.")
    else:
        messages.error(request, "Upload failed.")
    return redirect(p.get_absolute_url())


@login_required
@permission_required("crm.delete_document", raise_exception=True)
@require_POST
def document_delete(request, pk):
    d = get_object_or_404(Document, pk=pk)
    pid = d.passenger_id
    d.file.delete(save=False)
    d.delete()
    return redirect("passenger_detail", pk=pid)


# ---------- Groups ----------

@login_required
def group_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Group.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(destination__icontains=q))
    return render(request, "crm/group_list.html", {"groups": qs, "q": q})


@login_required
@permission_required("crm.add_group", raise_exception=True)
def group_create(request):
    form = GroupForm(request.POST or None)
    if form.is_valid():
        g = form.save()
        messages.success(request, "Group created.")
        return redirect(g.get_absolute_url())
    return render(request, "crm/group_form.html", {"form": form, "title": "New Group"})


@login_required
def group_detail(request, pk):
    g = get_object_or_404(Group, pk=pk)
    add_form = GroupMembershipForm()
    return render(request, "crm/group_detail.html", {"g": g, "add_form": add_form})


@login_required
@permission_required("crm.change_group", raise_exception=True)
def group_edit(request, pk):
    g = get_object_or_404(Group, pk=pk)
    form = GroupForm(request.POST or None, instance=g)
    if form.is_valid():
        form.save()
        return redirect(g.get_absolute_url())
    return render(request, "crm/group_form.html", {"form": form, "title": "Edit Group"})


@login_required
@permission_required("crm.delete_group", raise_exception=True)
@require_POST
def group_delete(request, pk):
    get_object_or_404(Group, pk=pk).delete()
    return redirect("group_list")


@login_required
@permission_required("crm.add_groupmembership", raise_exception=True)
@require_POST
def group_add_member(request, pk):
    g = get_object_or_404(Group, pk=pk)
    form = GroupMembershipForm(request.POST)
    if form.is_valid():
        m = form.save(commit=False)
        m.group = g
        try:
            m.save()
            messages.success(request, "Member added.")
        except Exception:
            messages.error(request, "Already a member.")
    return redirect(g.get_absolute_url())


@login_required
@permission_required("crm.delete_groupmembership", raise_exception=True)
@require_POST
def group_remove_member(request, pk, passenger_id):
    GroupMembership.objects.filter(group_id=pk, passenger_id=passenger_id).delete()
    return redirect("group_detail", pk=pk)


# ---------- Bookings ----------

@login_required
def booking_list(request):
    q = (request.GET.get("q") or "").strip()
    status = request.GET.get("status") or ""
    service = request.GET.get("service") or ""
    qs = Booking.objects.select_related("passenger", "group")
    if q:
        qs = qs.filter(
            Q(reference__icontains=q)
            | Q(passenger__full_name__icontains=q)
            | Q(passenger__passport_number__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    if service:
        qs = qs.filter(service_type=service)
    return render(request, "crm/booking_list.html", {
        "bookings": qs[:500], "q": q, "status": status, "service": service,
        "service_choices": SERVICE_CHOICES,
    })


@login_required
@permission_required("crm.add_booking", raise_exception=True)
def booking_create(request):
    form = BookingForm(request.POST or None)
    if form.is_valid():
        b = form.save(commit=False)
        b.created_by = request.user
        b.save()
        messages.success(request, f"Booking {b.reference} created.")
        return redirect(b.get_absolute_url())
    return render(request, "crm/booking_form.html", {"form": form, "title": "New Booking"})


@login_required
def booking_detail(request, pk):
    b = get_object_or_404(Booking.objects.select_related("passenger", "group"), pk=pk)
    pay_form = PaymentForm()
    return render(request, "crm/booking_detail.html", {"b": b, "pay_form": pay_form})


@login_required
@permission_required("crm.change_booking", raise_exception=True)
def booking_edit(request, pk):
    b = get_object_or_404(Booking, pk=pk)
    form = BookingForm(request.POST or None, instance=b)
    if form.is_valid():
        form.save()
        return redirect(b.get_absolute_url())
    return render(request, "crm/booking_form.html", {"form": form, "title": "Edit Booking"})


@login_required
@permission_required("crm.delete_booking", raise_exception=True)
@require_POST
def booking_delete(request, pk):
    get_object_or_404(Booking, pk=pk).delete()
    return redirect("booking_list")


@login_required
@permission_required("crm.add_payment", raise_exception=True)
@require_POST
def payment_create(request, pk):
    b = get_object_or_404(Booking, pk=pk)
    form = PaymentForm(request.POST)
    if form.is_valid():
        p = form.save(commit=False)
        p.booking = b
        p.received_by = request.user
        p.save()
        messages.success(request, "Payment recorded.")
    else:
        messages.error(request, "Invalid payment.")
    return redirect(b.get_absolute_url())


# ---------- Suppliers ----------

@login_required
def supplier_list(request):
    return render(request, "crm/supplier_list.html", {"suppliers": Supplier.objects.all()})


@login_required
@permission_required("crm.add_supplier", raise_exception=True)
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        s = form.save()
        return redirect("supplier_detail", pk=s.pk)
    return render(request, "crm/supplier_form.html", {"form": form, "title": "New Supplier"})


@login_required
def supplier_detail(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    pay_form = SupplierPaymentForm(initial={"supplier": s})
    return render(request, "crm/supplier_detail.html", {"s": s, "pay_form": pay_form})


@login_required
@permission_required("crm.change_supplier", raise_exception=True)
def supplier_edit(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=s)
    if form.is_valid():
        form.save()
        return redirect("supplier_detail", pk=s.pk)
    return render(request, "crm/supplier_form.html", {"form": form, "title": "Edit Supplier"})


@login_required
@permission_required("crm.add_supplierpayment", raise_exception=True)
@require_POST
def supplier_payment_create(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    form = SupplierPaymentForm(request.POST)
    if form.is_valid():
        p = form.save(commit=False)
        p.supplier = s
        p.save()
        messages.success(request, "Supplier payment recorded.")
    return redirect("supplier_detail", pk=s.pk)


# ---------- Reports / Exports ----------

def _excel_response(filename):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_passengers_excel(request):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Passengers"
    headers = ["Full Name", "Passport #", "CNIC", "Passport Expiry", "Visa Expiry", "Mobile", "Email"]
    ws.append(headers)
    for p in Passenger.objects.all():
        ws.append([
            p.full_name, p.passport_number, p.cnic,
            p.passport_expiry.isoformat() if p.passport_expiry else "",
            p.visa_expiry.isoformat() if p.visa_expiry else "",
            p.mobile, p.email,
        ])
    resp = _excel_response("passengers.xlsx")
    wb.save(resp)
    return resp


@login_required
def export_passengers_pdf(request):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), title="Passenger List")
    styles = getSampleStyleSheet()
    elements = [Paragraph("Passenger List", styles["Title"]), Spacer(1, 12)]
    data = [["#", "Name", "Passport", "CNIC", "P. Expiry", "V. Expiry", "Mobile"]]
    for i, p in enumerate(Passenger.objects.all(), 1):
        data.append([
            i, p.full_name, p.passport_number, p.cnic,
            p.passport_expiry or "", p.visa_expiry or "", p.mobile,
        ])
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)
    doc.build(elements)
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename="passengers.pdf")


@login_required
def booking_invoice_pdf(request, pk):
    b = get_object_or_404(Booking, pk=pk)
    return _booking_pdf(request, b, kind="invoice")


@login_required
def payment_receipt_pdf(request, pk, payment_id):
    b = get_object_or_404(Booking, pk=pk)
    payment = get_object_or_404(Payment, pk=payment_id, booking=b)
    return _booking_pdf(request, b, kind="receipt", payment=payment)


def _booking_pdf(request, b, kind="invoice", payment=None):
    from django.conf import settings
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=kind.title())
    styles = getSampleStyleSheet()
    el = []

    el.append(Paragraph(f"<b>{settings.AGENCY_NAME}</b>", styles["Title"]))
    el.append(Paragraph(settings.AGENCY_ADDRESS, styles["Normal"]))
    el.append(Paragraph(f"Phone: {settings.AGENCY_PHONE} &nbsp;&nbsp; Email: {settings.AGENCY_EMAIL}", styles["Normal"]))
    el.append(Spacer(1, 12))

    title = "INVOICE" if kind == "invoice" else "PAYMENT RECEIPT"
    el.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))

    info = [
        ["Reference", b.reference, "Date", timezone.now().date().isoformat()],
        ["Customer", b.passenger.full_name, "Passport", b.passenger.passport_number or "-"],
        ["Service", b.get_service_type_display(), "Travel Date", str(b.travel_date or "-")],
    ]
    t = Table(info, colWidths=[80, 180, 80, 180])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    el.append(t)
    el.append(Spacer(1, 12))

    if kind == "invoice":
        rows = [
            ["Description", "Amount"],
            [b.description or b.get_service_type_display(), f"{b.package_cost:.2f}"],
            ["Discount", f"-{b.discount:.2f}"],
            ["Net Total", f"{b.net_total:.2f}"],
            ["Received", f"{b.total_received:.2f}"],
            ["Balance Due", f"{b.balance_due:.2f}"],
        ]
    else:
        rows = [
            ["Item", "Detail"],
            ["Amount Received", f"{payment.amount:.2f}"],
            ["Method", payment.get_method_display()],
            ["Date", str(payment.received_on)],
            ["Reference", payment.reference or "-"],
            ["Booking Net Total", f"{b.net_total:.2f}"],
            ["Balance After", f"{b.balance_due:.2f}"],
        ]

    t2 = Table(rows, colWidths=[300, 200])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    el.append(t2)
    el.append(Spacer(1, 24))
    el.append(Paragraph("Thank you for choosing us.", styles["Italic"]))

    doc.build(el)
    buf.seek(0)
    fname = f"{kind}-{b.reference}.pdf"
    return FileResponse(buf, as_attachment=True, filename=fname)


@login_required
def financial_report(request):
    bookings = Booking.objects.select_related("passenger").exclude(status="CANCELLED")
    total_billed = bookings.aggregate(s=Sum("package_cost"))["s"] or Decimal("0")
    total_disc = bookings.aggregate(s=Sum("discount"))["s"] or Decimal("0")
    total_received = Payment.objects.filter(booking__in=bookings).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    supplier_paid = SupplierPayment.objects.aggregate(s=Sum("amount"))["s"] or Decimal("0")
    return render(request, "crm/financial_report.html", {
        "bookings": bookings[:200],
        "total_billed": total_billed,
        "total_disc": total_disc,
        "total_received": total_received,
        "outstanding": total_billed - total_disc - total_received,
        "supplier_paid": supplier_paid,
    })


@login_required
def export_financial_excel(request):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bookings"
    ws.append(["Reference", "Customer", "Service", "Package", "Discount", "Net", "Received", "Balance", "Status"])
    for b in Booking.objects.select_related("passenger"):
        ws.append([
            b.reference, b.passenger.full_name, b.get_service_type_display(),
            float(b.package_cost), float(b.discount), float(b.net_total),
            float(b.total_received), float(b.balance_due), b.get_status_display(),
        ])
    ws2 = wb.create_sheet("Supplier Payments")
    ws2.append(["Date", "Supplier", "Amount", "Method", "Booking", "Reference"])
    for sp in SupplierPayment.objects.select_related("supplier", "booking"):
        ws2.append([
            sp.paid_on.isoformat(), sp.supplier.name, float(sp.amount),
            sp.get_method_display(), sp.booking.reference if sp.booking else "",
            sp.reference,
        ])
    resp = _excel_response("financial_report.xlsx")
    wb.save(resp)
    return resp

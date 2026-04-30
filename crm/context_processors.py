from django.conf import settings


def agency_branding(request):
    return {
        "AGENCY_NAME": settings.AGENCY_NAME,
        "AGENCY_ADDRESS": settings.AGENCY_ADDRESS,
        "AGENCY_PHONE": settings.AGENCY_PHONE,
        "AGENCY_EMAIL": settings.AGENCY_EMAIL,
    }

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission


@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    if sender.name != "crm":
        return
    for role in ("Admin", "Staff"):
        Group.objects.get_or_create(name=role)
    # Admins get all CRM perms; Staff gets view/add/change but not delete on financial models.
    try:
        admin_group = Group.objects.get(name="Admin")
        staff_group = Group.objects.get(name="Staff")
        crm_perms = Permission.objects.filter(content_type__app_label="crm")
        admin_group.permissions.set(crm_perms)
        staff_perms = crm_perms.exclude(codename__startswith="delete_")
        staff_group.permissions.set(staff_perms)
    except Permission.DoesNotExist:
        pass

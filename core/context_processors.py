from django.conf import settings


def site_contacts(request):
    """Делает контакты сайта доступными во всех шаблонах как {{ site_contacts }}."""
    return {"site_contacts": settings.SITE_CONTACTS}
from django.contrib import admin
from .models import ChurchMember, GuestInformation


@admin.register(ChurchMember)
class ChurchMemberAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "mobile_phone",
        "membership_date",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "mobile_phone",
    )
    list_filter = (
        "marital_status",
        "membership_date",
    )


@admin.register(GuestInformation)
class GuestInformationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "mobile_phone",
        "visit_date",
    )
    search_fields = (
        "full_name",
        "email",
        "mobile_phone",
    )
    list_filter = (
        "visit_date",
    )

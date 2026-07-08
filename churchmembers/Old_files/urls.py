from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("register/", views.churchmembers, name="churchmembers"),
    path("members/", views.member_list, name="member_list"),
    path("members/edit/<int:member_id>/", views.edit_member, name="edit_member"),
    path("members/delete/<int:member_id>/", views.delete_member, name="delete_member"),
    path("members/export/excel/", views.export_members_excel, name="export_members_excel"),
    path("attendance/", views.mark_attendance, name="mark_attendance"),
    path("attendance/statistics/", views.attendance_statistics, name="attendance_statistics"),
    path("guest_information/", views.guest_information, name="guest_information"),
    path("guests/", views.guest_records, name="guest_records"),
    path("guests/<int:guest_id>/",views.guest_detail,name="guest_detail",),
    path("guests/<int:guest_id>/edit/",views.edit_guest,name="edit_guest",),
    path("guests/<int:guest_id>/delete/",views.delete_guest,name="delete_guest",),
]

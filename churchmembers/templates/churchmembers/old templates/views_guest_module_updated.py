from datetime import date
import openpyxl
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

#from .models import Attendance, ChurchMember, GuestInformation

from .models import (
    Address,
    Attendance,
    ChurchMember,
    Congregation,
    GuestInformation,
    Ministry,
    WorshipArea,
)

from .models import ChurchMember, Address, Congregation, Ministry, WorshipArea

def welcome(request):
    return render(request, "churchmembers/welcome.html")



def churchmembers(request):
    congregations = Congregation.objects.all().order_by("name")

    if request.method == "POST":
        selected_congregation_id = request.POST.get("originating_congregation")
        new_congregation_name = request.POST.get(
            "new_originating_congregation", ""
        ).strip()

        originating_congregation = None

        if selected_congregation_id:
            originating_congregation = Congregation.objects.get(
                id=selected_congregation_id
            )
        elif new_congregation_name:
            originating_congregation, _ = Congregation.objects.get_or_create(
                name=new_congregation_name
            )

        address = Address.objects.create(
            address_line1=request.POST.get("address_line1"),
            address_line2=request.POST.get("address_line2"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            zip_code=request.POST.get("zip_code"),
        )

        member = ChurchMember.objects.create(
            first_name=request.POST.get("first_name"),
            middle_name=request.POST.get("middle_name"),
            last_name=request.POST.get("last_name"),
            preferred_name=request.POST.get("preferred_name"),

            address=address,

            home_phone=request.POST.get("home_phone"),
            mobile_phone=request.POST.get("mobile_phone"),
            email=request.POST.get("email"),

            date_of_birth=request.POST.get("date_of_birth") or None,
            baptismal_date=request.POST.get("baptismal_date") or None,

            membership_date=request.POST.get("membership_date") or None,
            transfer_date=request.POST.get("transfer_date") or None,

            originating_congregation=originating_congregation,
            previous_congregation_notes=request.POST.get(
                "previous_congregation_notes"
            ),

            moved_to_area_date=request.POST.get("moved_to_area_date") or None,
            lives_with=request.POST.get("lives_with"),

            marital_status=request.POST.get("marital_status") or None,
            was_previously_married=bool(
                request.POST.get("was_previously_married")
            ),
            has_children=bool(request.POST.get("has_children")),
            children_in_congregation=request.POST.get(
                "children_in_congregation"
            ) or None,
        )

        selected_ministries = request.POST.getlist("ministries")
        for ministry_name in selected_ministries:
            ministry, _ = Ministry.objects.get_or_create(name=ministry_name)
            member.ministries.add(ministry)

        selected_worship_areas = request.POST.getlist("worship_areas")
        for worship_name in selected_worship_areas:
            worship_area, _ = WorshipArea.objects.get_or_create(name=worship_name)
            member.worship_areas.add(worship_area)

        messages.success(request, "Member registered successfully.")
        return redirect("member_list")

    return render(
        request,
        "churchmembers/registration.html",
        {
            "congregations": congregations,
        },
    )


def member_list(request):
    query = request.GET.get("q", "").strip()
    mychurchmembers = ChurchMember.objects.all().order_by("-created_at")

    if query:
        mychurchmembers = mychurchmembers.filter(
            Q(firstname__icontains=query)
            | Q(lastname__icontains=query)
            | Q(email__icontains=query)
            | Q(cell_phone__icontains=query)
            | Q(address__icontains=query)
        ).order_by("-created_at")

    return render(
        request,
        "churchmembers/RegisteredMembers.html",
        {
            "mychurchmembers": mychurchmembers,
            "query": query,
        },
    )


def edit_member(request, member_id):
    member = get_object_or_404(ChurchMember, id=member_id)

    if request.method == "POST":
        member.firstname = request.POST.get("firstname")
        member.lastname = request.POST.get("lastname")
        member.address = request.POST.get("address")
        member.home_phone = request.POST.get("home_phone")
        member.cell_phone = request.POST.get("cell_phone")
        member.email = request.POST.get("email")
        member.birthday = request.POST.get("birthday") or None
        member.baptismal_date = request.POST.get("baptismal_date") or None
        member.originating_congregation = request.POST.get("originating_congregation")
        member.membership_date = request.POST.get("membership_date") or None
        member.old_congregation_contact = request.POST.get("old_congregation_contact")
        member.move_date = request.POST.get("move_date")
        member.live_with = request.POST.get("live_with")
        member.married_now = request.POST.get("married_now")
        member.married_before = request.POST.get("married_before")
        member.children = request.POST.get("children")
        member.children_in_congregation = request.POST.get("children_in_congregation") or None
        member.ministries = ", ".join(request.POST.getlist("ministries[]"))
        member.worship_areas = ", ".join(request.POST.getlist("worship[]"))
        member.save()

        messages.success(request, "Member updated successfully.")
        return redirect("member_list")

    return render(
        request,
        "churchmembers/EditMember.html",
        {
            "member": member,
        },
    )


def delete_member(request, member_id):
    member = get_object_or_404(ChurchMember, id=member_id)

    if request.method == "POST":
        member.delete()
        messages.success(request, "Member deleted successfully.")
        return redirect("member_list")

    return render(
        request,
        "churchmembers/DeleteMember.html",
        {
            "member": member,
        },
    )


def export_members_excel(request):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Registered Members"

    headers = [
        "First Name",
        "Last Name",
        "Email",
        "Cell Phone",
        "Home Phone",
        "Address",
        "Birthday",
        "Baptismal Date",
        "Originating Congregation",
        "Membership Date",
        "Old Congregation Contact",
        "Move Date",
        "Live With",
        "Married Now",
        "Married Before",
        "Children",
        "Children In Congregation",
        "Ministries",
        "Worship Areas",
        "Created At",
    ]

    worksheet.append(headers)

    members = ChurchMember.objects.all().order_by("-created_at")

    for member in members:
        worksheet.append(
            [
                member.firstname,
                member.lastname,
                member.email,
                member.cell_phone,
                member.home_phone,
                member.address,
                member.birthday.strftime("%Y-%m-%d") if member.birthday else "",
                member.baptismal_date.strftime("%Y-%m-%d") if member.baptismal_date else "",
                member.originating_congregation,
                member.membership_date.strftime("%Y-%m-%d") if member.membership_date else "",
                member.old_congregation_contact,
                member.move_date,
                member.live_with,
                member.married_now,
                member.married_before,
                member.children,
                member.children_in_congregation,
                member.ministries,
                member.worship_areas,
                member.created_at.strftime("%Y-%m-%d %H:%M:%S") if member.created_at else "",
            ]
        )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="registered_members.xlsx"'

    workbook.save(response)
    return response


def mark_attendance(request):
    members = ChurchMember.objects.all().order_by("first_name", "last_name")
    selected_date = request.POST.get("date") or date.today().isoformat()

    if request.method == "POST":
        for member in members:
            status = request.POST.get(f"status_{member.id}", "Absent")

            Attendance.objects.update_or_create(
                member=member,
                date=selected_date,
                defaults={"status": status},
            )

        messages.success(request, "Attendance saved successfully.")
        return redirect("mark_attendance")

    return render(
        request,
        "churchmembers/attendance.html",
        {
            "members": members,
            "selected_date": selected_date,
        },
    )


def attendance_statistics(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    attendance_records = Attendance.objects.all()

    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)

    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)

    total_records = attendance_records.count()
    in_person_count = attendance_records.filter(status="In Person").count()
    zoom_count = attendance_records.filter(status="Zoom").count()
    absent_count = attendance_records.filter(status="Absent").count()
    excused_count = attendance_records.filter(status="Excused").count()
    late_count = attendance_records.filter(status="Late").count()

    member_stats = []

    members = ChurchMember.objects.all().order_by("first_name", "last_name")

    for member in members:
        member_attendance = attendance_records.filter(member=member)

        in_person = member_attendance.filter(status="In Person").count()
        zoom = member_attendance.filter(status="Zoom").count()
        absent = member_attendance.filter(status="Absent").count()
        excused = member_attendance.filter(status="Excused").count()
        late = member_attendance.filter(status="Late").count()

        member_stats.append(
            {
                "member": member,
                "in_person": in_person,
                "zoom": zoom,
                "absent": absent,
                "excused": excused,
                "late": late,
                "total_present": in_person + zoom + late,
            }
        )

    return render(
        request,
        "churchmembers/attendance_statistics.html",
        {
            "total_records": total_records,
            "in_person_count": in_person_count,
            "zoom_count": zoom_count,
            "absent_count": absent_count,
            "excused_count": excused_count,
            "late_count": late_count,
            "member_stats": member_stats,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


def guest_information(request):
    members = ChurchMember.objects.all().order_by("first_name", "last_name")

    if request.method == "POST":
        GuestInformation.objects.create(
            visit_date=request.POST.get("visit_date") or None,

            first_name=request.POST.get("first_name"),
            middle_name=request.POST.get("middle_name"),
            surname=request.POST.get("surname"),
            preferred_name=request.POST.get("preferred_name"),

            home_phone=request.POST.get("home_phone"),
            mobile_phone=request.POST.get("mobile_phone"),
            email=request.POST.get("email"),

            preferred_contact_method=request.POST.get("preferred_contact_method") or None,
            consent_to_contact=bool(request.POST.get("consent_to_contact")),

            visit_type=request.POST.get("visit_type") or None,
            invitation_source=request.POST.get("invitation_source") or None,
            invited_by_member_id=request.POST.get("invited_by_member") or None,
            invitation_notes=request.POST.get("invitation_notes"),

            new_to_area=bool(request.POST.get("new_to_area")),
            would_like_visit=bool(request.POST.get("would_like_visit")),
            would_like_more_info=bool(request.POST.get("would_like_more_info")),

            interested_in_membership=bool(request.POST.get("interested_in_membership")),
            interested_in_bible_study=bool(request.POST.get("interested_in_bible_study")),
            interested_in_children_ministry=bool(request.POST.get("interested_in_children_ministry")),
            interested_in_youth_ministry=bool(request.POST.get("interested_in_youth_ministry")),

            life_stage=request.POST.get("life_stage") or None,
            age_group=request.POST.get("age_group") or None,
            has_children_at_home=bool(request.POST.get("has_children_at_home")),
            number_of_children=request.POST.get("number_of_children") or None,

            home_church=request.POST.get("home_church"),
            prayer_request=request.POST.get("prayer_request"),
            notes=request.POST.get("notes"),

            assigned_follow_up_person_id=request.POST.get("assigned_follow_up_person") or None,
            follow_up_completed=bool(request.POST.get("follow_up_completed")),
            follow_up_date=request.POST.get("follow_up_date") or None,
        )

        messages.success(request, "Guest information submitted successfully.")
        return redirect("guest_information")

    return render(
        request,
        "churchmembers/GuestInformation.html",
        {
            "members": members,
            "age_group_choices": GuestInformation.AGE_GROUP_CHOICES,
            "visit_type_choices": GuestInformation.VISIT_TYPE_CHOICES,
            "life_stage_choices": GuestInformation.LIFE_STAGE_CHOICES,
            "invitation_source_choices": GuestInformation.INVITATION_SOURCE_CHOICES,
            "contact_method_choices": GuestInformation.CONTACT_METHOD_CHOICES,
        },
    )



def guest_records(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    search = request.GET.get("search", "").strip()

    guests = GuestInformation.objects.select_related(
        "invited_by_member",
        "assigned_follow_up_person",
        "address",
    ).order_by("-visit_date", "-created_at")

    if start_date:
        guests = guests.filter(visit_date__gte=start_date)

    if end_date:
        guests = guests.filter(visit_date__lte=end_date)

    if search:
        guests = guests.filter(
            Q(first_name__icontains=search)
            | Q(middle_name__icontains=search)
            | Q(surname__icontains=search)
            | Q(preferred_name__icontains=search)
            | Q(full_name__icontains=search)
            | Q(email__icontains=search)
            | Q(home_phone__icontains=search)
            | Q(mobile_phone__icontains=search)
            | Q(home_church__icontains=search)
        )

    total_guests = guests.count()
    first_time_count = guests.filter(visit_type="First Time").count()
    returning_count = guests.filter(visit_type="Returning").count()
    visit_request_count = guests.filter(would_like_visit=True).count()
    info_request_count = guests.filter(would_like_more_info=True).count()
    membership_interest_count = guests.filter(interested_in_membership=True).count()
    bible_study_interest_count = guests.filter(interested_in_bible_study=True).count()
    follow_up_pending_count = guests.filter(follow_up_completed=False).count()
    follow_up_completed_count = guests.filter(follow_up_completed=True).count()

    return render(
        request,
        "churchmembers/guest_records.html",
        {
            "guests": guests,
            "total_guests": total_guests,
            "first_time_count": first_time_count,
            "returning_count": returning_count,
            "visit_request_count": visit_request_count,
            "info_request_count": info_request_count,
            "membership_interest_count": membership_interest_count,
            "bible_study_interest_count": bible_study_interest_count,
            "follow_up_pending_count": follow_up_pending_count,
            "follow_up_completed_count": follow_up_completed_count,
            "start_date": start_date,
            "end_date": end_date,
            "search": search,
        },
    )





def guest_detail(request, guest_id):
    guest = get_object_or_404(GuestInformation, id=guest_id)

    return render(
        request,
        "churchmembers/guest_detail.html",
        {"guest": guest},
    )


def edit_guest(request, guest_id):
    guest = get_object_or_404(GuestInformation, id=guest_id)
    members = ChurchMember.objects.all().order_by("first_name", "last_name")

    if request.method == "POST":
        guest.visit_date = request.POST.get("visit_date") or None
        guest.first_name = request.POST.get("first_name")
        guest.middle_name = request.POST.get("middle_name")
        guest.surname = request.POST.get("surname")
        guest.preferred_name = request.POST.get("preferred_name")
        guest.home_phone = request.POST.get("home_phone")
        guest.mobile_phone = request.POST.get("mobile_phone")
        guest.email = request.POST.get("email")
        guest.preferred_contact_method = request.POST.get("preferred_contact_method") or None
        guest.consent_to_contact = bool(request.POST.get("consent_to_contact"))
        guest.visit_type = request.POST.get("visit_type") or None
        guest.invitation_source = request.POST.get("invitation_source") or None
        guest.invited_by_member_id = request.POST.get("invited_by_member") or None
        guest.invitation_notes = request.POST.get("invitation_notes")
        guest.new_to_area = bool(request.POST.get("new_to_area"))
        guest.would_like_visit = bool(request.POST.get("would_like_visit"))
        guest.would_like_more_info = bool(request.POST.get("would_like_more_info"))
        guest.interested_in_membership = bool(request.POST.get("interested_in_membership"))
        guest.interested_in_bible_study = bool(request.POST.get("interested_in_bible_study"))
        guest.interested_in_children_ministry = bool(request.POST.get("interested_in_children_ministry"))
        guest.interested_in_youth_ministry = bool(request.POST.get("interested_in_youth_ministry"))
        guest.life_stage = request.POST.get("life_stage") or None
        guest.age_group = request.POST.get("age_group") or None
        guest.has_children_at_home = bool(request.POST.get("has_children_at_home"))
        guest.number_of_children = request.POST.get("number_of_children") or None
        guest.home_church = request.POST.get("home_church")
        guest.prayer_request = request.POST.get("prayer_request")
        guest.notes = request.POST.get("notes")
        guest.assigned_follow_up_person_id = request.POST.get("assigned_follow_up_person") or None
        guest.follow_up_completed = bool(request.POST.get("follow_up_completed"))
        guest.follow_up_date = request.POST.get("follow_up_date") or None
        guest.save()

        messages.success(request, "Guest updated successfully.")
        return redirect("guest_records")

    return render(
        request,
        "churchmembers/EditGuest.html",
        {
            "guest": guest,
            "members": members,
            "age_group_choices": GuestInformation.AGE_GROUP_CHOICES,
            "visit_type_choices": GuestInformation.VISIT_TYPE_CHOICES,
            "life_stage_choices": GuestInformation.LIFE_STAGE_CHOICES,
            "invitation_source_choices": GuestInformation.INVITATION_SOURCE_CHOICES,
            "contact_method_choices": GuestInformation.CONTACT_METHOD_CHOICES,
        },
    )


def delete_guest(request, guest_id):
    guest = get_object_or_404(GuestInformation, id=guest_id)

    if request.method == "POST":
        guest.delete()
        messages.success(request, "Guest deleted successfully.")
        return redirect("guest_records")

    return render(
        request,
        "churchmembers/DeleteGuest.html",
        {"guest": guest},
    )

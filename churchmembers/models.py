from django.db import models

# models.py

class Ministry(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="ministries/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name




class Address(models.Model):
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default="United States")

    def __str__(self):
        return f"{self.address_line1}, {self.city}"


class Congregation(models.Model):
    name = models.CharField(max_length=200)
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="congregations"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    pastor_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name




class WorshipArea(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ChurchMember(models.Model):
    MARITAL_STATUS_CHOICES = [
        ("Single", "Single"),
        ("Married", "Married"),
        ("Widowed", "Widowed"),
        ("Divorced", "Divorced"),
        ("Separated", "Separated"),
    ]

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)

    preferred_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Name the member prefers to be called."
    )

    photo = models.ImageField(
        upload_to="member_photos/",
        blank=True,
        null=True
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="church_members"
    )

    home_phone = models.CharField(max_length=20, blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)
    baptismal_date = models.DateField(blank=True, null=True)

    membership_date = models.DateField(blank=True, null=True)
    transfer_date = models.DateField(blank=True, null=True)

    originating_congregation = models.ForeignKey(
        Congregation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="transferred_members"
    )

    previous_congregation_notes = models.TextField(blank=True, null=True)

    moved_to_area_date = models.DateField(blank=True, null=True)
    lives_with = models.CharField(max_length=200, blank=True, null=True)

    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        null=True
    )

    was_previously_married = models.BooleanField(default=False)
    has_children = models.BooleanField(default=False)
    children_in_congregation = models.PositiveIntegerField(blank=True, null=True)

    ministries = models.ManyToManyField(
        Ministry,
        blank=True,
        related_name="members"
    )

    worship_areas = models.ManyToManyField(
        WorshipArea,
        blank=True,
        related_name="members"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return " ".join([name for name in names if name])

    @property
    def display_name(self):
        if self.preferred_name:
            return f"{self.preferred_name} {self.last_name}"
        return self.full_name

    def __str__(self):
        return self.display_name


class Attendance(models.Model):
    ATTENDANCE_STATUS_CHOICES = [
        ("Absent", "Absent"),
        ("In Person", "In Person"),
        ("Zoom", "Zoom"),
        ("Excused", "Excused"),
        ("Late", "Late"),
    ]

    member = models.ForeignKey(
        ChurchMember,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        default="Absent"
    )

    note = models.CharField(max_length=255, blank=True, null=True)

    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "member"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "date"],
                name="unique_member_attendance_per_date"
            )
        ]

    def __str__(self):
        return f"{self.member} - {self.date} - {self.status}"


class GuestInformation(models.Model):
    AGE_GROUP_CHOICES = [
        ("Under 20", "Under 20"),
        ("20s", "20s"),
        ("30s", "30s"),
        ("40s", "40s"),
        ("50s", "50s"),
        ("60s", "60s"),
        ("70s+", "70s+"),
    ]

    VISIT_TYPE_CHOICES = [
        ("First Time", "First Time"),
        ("Returning", "Returning"),
        ("Other", "Other"),
    ]

    LIFE_STAGE_CHOICES = [
        ("Single", "Single"),
        ("Married", "Married"),
        ("Single Parent", "Single Parent"),
        ("Widowed", "Widowed"),
        ("College Student", "College Student"),
        ("High School Student", "High School Student"),
        ("Middle School Student", "Middle School Student"),
    ]

    INVITATION_SOURCE_CHOICES = [
        ("Invited by Member", "Invited by Member"),
        ("Came Voluntarily", "Came Voluntarily"),
        ("Church Outreach", "Church Outreach"),
        ("Online/Social Media", "Online/Social Media"),
        ("Other", "Other"),
    ]

    CONTACT_METHOD_CHOICES = [
        ("Phone", "Phone"),
        ("Email", "Email"),
        ("Text", "Text"),
        ("WhatsApp", "WhatsApp"),
        ("No Preference", "No Preference"),
    ]

    visit_date = models.DateField(blank=True, null=True)

    # Keep this temporarily so old records and migrations do not break.
    full_name = models.CharField(max_length=200, blank=True, null=True)

    # New separated name fields
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    surname = models.CharField(max_length=100, blank=True, null=True)
    preferred_name = models.CharField(max_length=100, blank=True, null=True)

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="guests",
    )

    home_phone = models.CharField(max_length=20, blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    preferred_contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        blank=True,
        null=True,
    )

    consent_to_contact = models.BooleanField(default=False)

    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPE_CHOICES,
        blank=True,
        null=True,
    )

    invitation_source = models.CharField(
        max_length=30,
        choices=INVITATION_SOURCE_CHOICES,
        blank=True,
        null=True,
    )

    invited_by_member = models.ForeignKey(
        ChurchMember,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="invited_guests",
    )

    invitation_notes = models.TextField(blank=True, null=True)

    new_to_area = models.BooleanField(default=False)
    would_like_visit = models.BooleanField(default=False)
    would_like_more_info = models.BooleanField(default=False)

    interested_in_membership = models.BooleanField(default=False)
    interested_in_bible_study = models.BooleanField(default=False)
    interested_in_children_ministry = models.BooleanField(default=False)
    interested_in_youth_ministry = models.BooleanField(default=False)

    life_stage = models.CharField(
        max_length=30,
        choices=LIFE_STAGE_CHOICES,
        blank=True,
        null=True,
    )

    age_group = models.CharField(
        max_length=20,
        choices=AGE_GROUP_CHOICES,
        blank=True,
        null=True,
    )

    has_children_at_home = models.BooleanField(default=False)
    number_of_children = models.PositiveIntegerField(blank=True, null=True)

    home_church = models.CharField(max_length=200, blank=True, null=True)

    prayer_request = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    assigned_follow_up_person = models.ForeignKey(
        ChurchMember,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="assigned_guest_followups",
    )

    follow_up_completed = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def display_name(self):
        names = [self.first_name, self.middle_name, self.surname]
        combined_name = " ".join([name for name in names if name])
        return combined_name or self.full_name or "Guest"

    class Meta:
        ordering = ["-visit_date", "surname", "first_name"]

    def __str__(self):
        return self.display_name



class MediaCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)


class Speaker(models.Model):
    name = models.CharField(max_length=120)
    title = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(upload_to="speakers/", blank=True)


class MediaItem(models.Model):
    MEDIA_TYPES = [
        ("video", "Video"),
        ("audio", "Audio"),
        ("livestream", "Livestream"),
        ("notes", "Notes"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(MediaCategory, on_delete=models.SET_NULL, null=True)
    media_type = models.CharField(max_length=30, choices=MEDIA_TYPES)
    scripture = models.CharField(max_length=150, blank=True)
    topic = models.CharField(max_length=100, blank=True)
    summary = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="media_thumbnails/", blank=True)
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)
    notes_file = models.FileField(upload_to="sermon_notes/", blank=True)
    date_published = models.DateField()
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    


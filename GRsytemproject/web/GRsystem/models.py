from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Profile(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('teaching_staff', 'Teaching Staff'),
        ('non_teaching_staff', 'Non-Teaching Staff'),
        ('grievance', 'Grievance Cell Member'),
    )
    COLLEGES = (
        ('College1', 'College 1'),
        ('College2', 'College 2'),
    )
    BRANCHES = (
        ('ComputerScience', 'Computer Science'),
        ('InformationScience', 'Information Science'),
        ('ElectronicsCommunication', 'Electronics & Communication'),
        ('Mechanical', 'Mechanical'),
    )
    phone_regex = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    collegename = models.CharField(max_length=50, choices=COLLEGES, blank=False)
    contactnumber = models.CharField(validators=[phone_regex], max_length=10, blank=True)
    type_user = models.CharField(max_length=25, default='student', choices=USER_TYPES)
    Branch = models.CharField(choices=BRANCHES, max_length=50, default='ComputerScience')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_type_user_display()})"

    class Meta:
        app_label = 'GRsystem'


class Complaint(models.Model):
    STATUS = ((1, 'Resolved'), (2, 'In Progress'), (3, 'Pending'))
    TYPES = (
        ('ClassRoom', 'Classroom'),
        ('Teacher', 'Teacher'),
        ('Management', 'Management'),
        ('College', 'College'),
        ('Other', 'Other'),
    )
    DEPARTMENTS = (
        ('ComputerScience', 'Computer Science'),
        ('InformationScience', 'Information Science'),
        ('ElectronicsCommunication', 'Electronics & Communication'),
        ('Mechanical', 'Mechanical'),
        ('Administration', 'Administration'),
        ('General', 'General'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Subject = models.CharField(max_length=200)
    Type_of_complaint = models.CharField(choices=TYPES, max_length=50)
    department = models.CharField(choices=DEPARTMENTS, max_length=50, blank=True, null=True)
    Description = models.TextField(max_length=4000)
    Time = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=3)
    remarks = models.TextField(blank=True, default='')

    def __str__(self):
        return f"GRV-{self.id:04d}: {self.Subject}"

    @property
    def complaint_id(self):
        return f"GRV-{self.id:04d}"

    class Meta:
        app_label = 'GRsystem'
        ordering = ['-Time']


class ComplaintHistory(models.Model):
    STATUS = ((1, 'Resolved'), (2, 'In Progress'), (3, 'Pending'))

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_status = models.IntegerField(choices=STATUS, null=True, blank=True)
    new_status = models.IntegerField(choices=STATUS)
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.complaint_id} — {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        app_label = 'GRsystem'
        ordering = ['-timestamp']
        verbose_name_plural = 'Complaint Histories'


class Grievance(models.Model):
    guser = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.guser)

    class Meta:
        app_label = 'GRsystem'

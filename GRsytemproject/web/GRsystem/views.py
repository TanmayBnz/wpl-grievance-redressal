from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from .models import Profile, Complaint, ComplaintHistory
from .forms import (
    UserRegisterForm, UserProfileform, ProfileUpdateForm,
    UserProfileUpdateform, ComplaintForm, StatusUpdateForm,
)
from .tokens import account_activation_token


# ─── Helpers ────────────────────────────────────────────────────────────────

def _send_mail_safe(subject, body, recipient):
    """Send mail silently — no crash if SMTP isn't configured."""
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@grs.local'
    send_mail(subject, body, from_email, [recipient], fail_silently=True)


def _require_grievance(request):
    """Return redirect if user is not a grievance member, else None."""
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    if request.user.profile.type_user != 'grievance':
        return redirect('dashboard')
    return None


def _require_student(request):
    """Return redirect if user is a grievance member, else None."""
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    if request.user.profile.type_user == 'grievance':
        return redirect('counter')
    return None


# ─── Public pages ───────────────────────────────────────────────────────────

def index(request):
    return render(request, 'GRsystem/home.html')


def aboutus(request):
    return render(request, 'GRsystem/aboutus.html')


def login_page(request):
    return render(request, 'GRsystem/login.html')


# ─── Auth / Registration ────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('login_redirect')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileform(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Send activation email
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )
            mail_body = render_to_string('GRsystem/account_activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            _send_mail_safe('Activate your GRS account', mail_body, user.email)

            return render(request, 'GRsystem/account_activation_sent.html', {'email': user.email})
    else:
        form = UserRegisterForm()
        profile_form = UserProfileform()

    return render(request, 'GRsystem/register.html', {'form': form, 'profile_form': profile_form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Account activated successfully. Welcome!')
        return redirect('login_redirect')

    messages.error(request, 'The activation link is invalid or has expired.')
    return redirect('signin')


@login_required
def login_redirect(request):
    if request.user.profile.type_user == 'grievance':
        return redirect('counter')
    return redirect('dashboard')


# ─── Student views ──────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    guard = _require_student(request)
    if guard:
        return guard

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateform(request.POST, instance=request.user.profile)
        if p_form.is_valid() and profile_form.is_valid():
            user = p_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateform(instance=request.user.profile)

    return render(request, 'GRsystem/dashboard.html', {
        'p_form': p_form,
        'profile_form': profile_form,
    })


@login_required
def complaints(request):
    guard = _require_student(request)
    if guard:
        return guard

    if request.method == 'POST':
        complaint_form = ComplaintForm(request.POST)
        if complaint_form.is_valid():
            instance = complaint_form.save(commit=False)
            instance.user = request.user
            instance.save()
            _send_mail_safe(
                'Grievance Received — GRS',
                f'Dear {request.user.get_full_name() or request.user.username},\n\n'
                f'Your grievance ({instance.complaint_id}) has been received and is under review.\n\n'
                f'Subject: {instance.Subject}\nCategory: {instance.get_Type_of_complaint_display()}\n\n'
                'We will update you on any progress. Please do not reply to this email.',
                request.user.email,
            )
            messages.success(request, f'Complaint {instance.complaint_id} submitted successfully.')
            return redirect('complaints')
    else:
        complaint_form = ComplaintForm()

    return render(request, 'GRsystem/comptotal.html', {'complaint_form': complaint_form})


@login_required
def complaint_list(request):
    guard = _require_student(request)
    if guard:
        return guard
    complaints_qs = Complaint.objects.filter(user=request.user).exclude(status=1)
    return render(request, 'GRsystem/Complaints.html', {'complaints': complaints_qs})


@login_required
def solved_list(request):
    guard = _require_student(request)
    if guard:
        return guard
    complaints_qs = Complaint.objects.filter(user=request.user, status=1)
    return render(request, 'GRsystem/solvedcomplaint.html', {'complaints': complaints_qs})


@login_required
def change_password(request):
    guard = _require_student(request)
    if guard:
        return guard

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
            return redirect('change_password')
        else:
            messages.warning(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'GRsystem/change_password.html', {'form': form})


# ─── Grievance officer views ─────────────────────────────────────────────────

@login_required
def counter(request):
    guard = _require_grievance(request)
    if guard:
        return guard

    total = Complaint.objects.count()
    unsolved = Complaint.objects.exclude(status=1).count()
    solved = Complaint.objects.filter(status=1).count()
    inprogress = Complaint.objects.filter(status=2).count()
    dataset = (
        Complaint.objects
        .values('Type_of_complaint')
        .annotate(
            total=Count('id'),
            solved=Count('id', filter=Q(status=1)),
            inprogress=Count('id', filter=Q(status=2)),
            pending=Count('id', filter=Q(status=3)),
        )
        .order_by('Type_of_complaint')
    )
    return render(request, 'GRsystem/counter.html', {
        'total': total,
        'unsolved': unsolved,
        'solved': solved,
        'inprogress': inprogress,
        'dataset': dataset,
    })


@login_required
def allcomplaints(request):
    guard = _require_grievance(request)
    if guard:
        return guard

    qs = Complaint.objects.exclude(status=1).select_related('user')
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    if category:
        qs = qs.filter(Type_of_complaint=category)
    if search:
        qs = qs.filter(
            Q(Type_of_complaint__icontains=search) |
            Q(Description__icontains=search) |
            Q(Subject__icontains=search) |
            Q(user__username__icontains=search)
        )

    if request.method == 'POST':
        cid = request.POST.get('cid')
        complaint = get_object_or_404(Complaint, id=cid)
        form = StatusUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            old_status = complaint.status
            obj = form.save()
            ComplaintHistory.objects.create(
                complaint=obj,
                changed_by=request.user,
                old_status=old_status,
                new_status=obj.status,
                remarks=form.cleaned_data.get('remarks', ''),
            )
            status_label = obj.get_status_display()
            _send_mail_safe(
                f'Grievance Update — {obj.complaint_id}',
                f'Dear {obj.user.get_full_name() or obj.user.username},\n\n'
                f'Your grievance ({obj.complaint_id}: {obj.Subject}) has been updated.\n\n'
                f'Status: {status_label}\n'
                + (f'Remarks: {obj.remarks}\n' if obj.remarks else '')
                + '\nPlease do not reply to this email.',
                obj.user.email,
            )
            messages.success(request, f'Complaint {obj.complaint_id} updated to "{status_label}".')
            return HttpResponseRedirect(reverse('allcomplaints'))
        else:
            messages.warning(request, 'Please correct the form errors.')
    else:
        form = StatusUpdateForm()

    return render(request, 'GRsystem/AllComplaints.html', {
        'complaints': qs,
        'form': form,
        'search': search,
        'category': category,
        'categories': Complaint.TYPES,
    })


@login_required
def solved_complaints(request):
    guard = _require_grievance(request)
    if guard:
        return guard

    qs = Complaint.objects.filter(status=1).select_related('user')
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    if category:
        qs = qs.filter(Type_of_complaint=category)
    if search:
        qs = qs.filter(
            Q(Type_of_complaint__icontains=search) |
            Q(Description__icontains=search) |
            Q(Subject__icontains=search)
        )

    if request.method == 'POST':
        cid = request.POST.get('cid')
        complaint = get_object_or_404(Complaint, id=cid)
        form = StatusUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            old_status = complaint.status
            obj = form.save()
            ComplaintHistory.objects.create(
                complaint=obj,
                changed_by=request.user,
                old_status=old_status,
                new_status=obj.status,
                remarks=form.cleaned_data.get('remarks', ''),
            )
            messages.success(request, f'Complaint {obj.complaint_id} updated.')
            return HttpResponseRedirect(reverse('solved'))
        else:
            messages.warning(request, 'Please correct the form errors.')
    else:
        form = StatusUpdateForm()

    return render(request, 'GRsystem/solved.html', {
        'complaints': qs,
        'form': form,
        'search': search,
        'categories': Complaint.TYPES,
    })


@login_required
def change_password_g(request):
    guard = _require_grievance(request)
    if guard:
        return guard

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
            return redirect('change_password_g')
        else:
            messages.warning(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'GRsystem/change_password_g.html', {'form': form})


# ─── PDF generation ──────────────────────────────────────────────────────────

def _build_pdf(complaint):
    """Return a PDF HttpResponse for the given complaint."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{complaint.complaint_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Heading1'], fontSize=16,
                                 spaceAfter=12, textColor=colors.HexColor('#1e2d3d'))
    label_style = ParagraphStyle('label', parent=styles['Normal'], fontSize=9,
                                 textColor=colors.grey, spaceBefore=10)
    value_style = ParagraphStyle('value', parent=styles['Normal'], fontSize=11)
    desc_style = ParagraphStyle('desc', parent=styles['Normal'], fontSize=10,
                                leading=16, spaceBefore=4)

    STATUS_LABELS = {1: 'Resolved', 2: 'In Progress', 3: 'Pending'}
    status_label = STATUS_LABELS.get(complaint.status, str(complaint.status))

    story = [
        Paragraph('Grievance Redressal System', title_style),
        Paragraph(f'Complaint Report — {complaint.complaint_id}', styles['Heading2']),
        Spacer(1, 0.4*cm),
    ]

    fields = [
        ('Submitted by', complaint.user.get_full_name() or complaint.user.username),
        ('Username', complaint.user.username),
        ('Date Filed', str(complaint.Time)),
        ('Category', complaint.get_Type_of_complaint_display()),
        ('Department', complaint.get_department_display() if complaint.department else '—'),
        ('Subject', complaint.Subject),
        ('Status', status_label),
    ]

    for label, value in fields:
        story.append(Paragraph(label, label_style))
        story.append(Paragraph(str(value), value_style))

    story.append(Paragraph('Description', label_style))
    story.append(Paragraph(complaint.Description or '—', desc_style))

    if complaint.remarks:
        story.append(Paragraph('Remarks from Grievance Cell', label_style))
        story.append(Paragraph(complaint.remarks, desc_style))

    history_qs = complaint.history.select_related('changed_by').order_by('timestamp')
    if history_qs.exists():
        story.append(Spacer(1, 0.6*cm))
        story.append(Paragraph('Status History', styles['Heading3']))
        STATUS_MAP = {1: 'Resolved', 2: 'In Progress', 3: 'Pending'}
        table_data = [['Date & Time', 'Changed By', 'From', 'To', 'Remarks']]
        for h in history_qs:
            table_data.append([
                h.timestamp.strftime('%Y-%m-%d %H:%M'),
                h.changed_by.username if h.changed_by else '—',
                STATUS_MAP.get(h.old_status, '—'),
                STATUS_MAP.get(h.new_status, '—'),
                h.remarks or '—',
            ])
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e2d3d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t)

    doc.build(story)
    return response


@login_required
def pdf_view(request):
    """Student downloads their own complaint PDF."""
    if request.method != 'POST':
        return redirect('list')
    cid = request.POST.get('cid')
    complaint = get_object_or_404(Complaint, id=cid, user=request.user)
    return _build_pdf(complaint)


@login_required
def pdf_viewer(request):
    """Grievance officer downloads any complaint PDF."""
    guard = _require_grievance(request)
    if guard:
        return guard
    if request.method != 'POST':
        return redirect('allcomplaints')
    cid = request.POST.get('cid')
    complaint = get_object_or_404(Complaint, id=cid)
    return _build_pdf(complaint)

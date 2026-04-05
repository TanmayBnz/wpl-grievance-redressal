from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('GRsystem', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add department to Complaint
        migrations.AddField(
            model_name='complaint',
            name='department',
            field=models.CharField(
                blank=True,
                choices=[
                    ('ComputerScience', 'Computer Science'),
                    ('InformationScience', 'Information Science'),
                    ('ElectronicsCommunication', 'Electronics & Communication'),
                    ('Mechanical', 'Mechanical'),
                    ('Administration', 'Administration'),
                    ('General', 'General'),
                ],
                max_length=50,
                null=True,
            ),
        ),
        # Add remarks to Complaint
        migrations.AddField(
            model_name='complaint',
            name='remarks',
            field=models.TextField(blank=True, default=''),
        ),
        # Add updated_at to Complaint
        migrations.AddField(
            model_name='complaint',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Change Time from auto_now to auto_now_add (filed date should not change)
        migrations.AlterField(
            model_name='complaint',
            name='Time',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Update status choices labels
        migrations.AlterField(
            model_name='complaint',
            name='status',
            field=models.IntegerField(
                choices=[(1, 'Resolved'), (2, 'In Progress'), (3, 'Pending')],
                default=3,
            ),
        ),
        # Update type choices
        migrations.AlterField(
            model_name='complaint',
            name='Type_of_complaint',
            field=models.CharField(
                choices=[
                    ('ClassRoom', 'Classroom'),
                    ('Teacher', 'Teacher'),
                    ('Management', 'Management'),
                    ('College', 'College'),
                    ('Other', 'Other'),
                ],
                max_length=50,
                null=True,
            ),
        ),
        # Update Profile type_user choices
        migrations.AlterField(
            model_name='profile',
            name='type_user',
            field=models.CharField(
                choices=[
                    ('student', 'Student'),
                    ('teaching_staff', 'Teaching Staff'),
                    ('non_teaching_staff', 'Non-Teaching Staff'),
                    ('grievance', 'Grievance Cell Member'),
                ],
                default='student',
                max_length=25,
            ),
        ),
        # Create ComplaintHistory
        migrations.CreateModel(
            name='ComplaintHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.IntegerField(
                    blank=True,
                    choices=[(1, 'Resolved'), (2, 'In Progress'), (3, 'Pending')],
                    null=True,
                )),
                ('new_status', models.IntegerField(
                    choices=[(1, 'Resolved'), (2, 'In Progress'), (3, 'Pending')],
                )),
                ('remarks', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('complaint', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='history',
                    to='GRsystem.complaint',
                )),
                ('changed_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name_plural': 'Complaint Histories',
                'ordering': ['-timestamp'],
            },
        ),
    ]

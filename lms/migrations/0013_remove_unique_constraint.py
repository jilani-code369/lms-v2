# Generated manually to remove unique constraint from sponsorship student field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0012_alter_sponsorship_student'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE lms_sponsorship DROP CONSTRAINT IF EXISTS lms_sponsorship_student_id_key;",
            reverse_sql="ALTER TABLE lms_sponsorship ADD CONSTRAINT lms_sponsorship_student_id_key UNIQUE (student_id);"
        ),
    ]

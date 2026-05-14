from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profesor',
            name='legajo',
        ),
    ]

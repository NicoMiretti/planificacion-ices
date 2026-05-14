from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instancias', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instanciapresentacion',
            name='anios_cursado',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Años de cursado incluidos (lista de enteros, ej: [1,2,3]). Vacío = todos los años.'
            ),
        ),
    ]

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('trades', '0006_add_validators_and_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculation',
            name='user',
            field=models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
                null=True,
                blank=True,
                default=None,
            ),
        ),
    ]

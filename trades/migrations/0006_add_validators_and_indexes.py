from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [
        ('trades', '0005_remove_calculationsnapshot_total_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                validators=[django.core.validators.MinValueValidator(0.01)]
            ),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='markup',
            field=models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(1000)
                ]
            ),
        ),
        migrations.AddIndex(
            model_name='calculationitem',
            index=models.Index(
                fields=['calculation'],
                name='calc_item_calc_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='calculation',
            index=models.Index(
                fields=['user', '-created_at'],
                name='calc_user_date_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='pricehistory',
            index=models.Index(
                fields=['item', '-changed_at'],
                name='price_hist_item_idx'
            ),
        ),
    ]
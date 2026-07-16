from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_product_color_freetext"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="discount_starts_on",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="discount_ends_on",
            field=models.DateField(blank=True, null=True),
        ),
    ]

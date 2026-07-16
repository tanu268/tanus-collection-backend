from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_product_categories_multicategory"),
    ]

    operations = [
        # color/border_color used to be locked to a hardcoded Color choices
        # list (red, maroon, pink, ... navy_blue, multicolor), which silently
        # rejected any custom or multi-word color name typed in the admin
        # (e.g. "Rama Green", "Peacock Blue"). They're now plain free-text
        # fields, so any color name is accepted.
        migrations.AlterField(
            model_name="product",
            name="color",
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="product",
            name="border_color",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

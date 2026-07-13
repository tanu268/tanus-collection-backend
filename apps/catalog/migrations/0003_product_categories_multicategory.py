from django.db import migrations, models


def migrate_category_to_categories(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    for product in Product.objects.all().only("id", "category_id"):
        if product.category_id:
            product.categories.add(product.category_id)


def migrate_categories_to_category(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    for product in Product.objects.all():
        first_category = product.categories.first()
        if first_category:
            product.category_id = first_category.id
            product.save(update_fields=["category"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_category_blurb_category_image"),
    ]

    operations = [
        # Step 1: add the new M2M field under a temporary related_name so it
        # doesn't clash with the old FK's related_name="products" while both
        # fields briefly coexist.
        migrations.AddField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(related_name="products_m2m_tmp", to="catalog.category"),
        ),
        # Step 2: copy existing category_id values across into the new M2M table.
        migrations.RunPython(
            migrate_category_to_categories,
            migrate_categories_to_category,
        ),
        # Step 3: drop the old FK column now that data has been migrated.
        migrations.RemoveField(
            model_name="product",
            name="category",
        ),
        # Step 4: rename the M2M field's related_name to the one the rest of
        # the app expects ("products"), now that there's no clash.
        migrations.AlterField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(related_name="products", to="catalog.category"),
        ),
    ]

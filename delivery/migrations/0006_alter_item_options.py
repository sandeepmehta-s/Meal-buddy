from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('delivery', '0005_customer_security_and_catalog_constraints'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['name']},
        ),
    ]

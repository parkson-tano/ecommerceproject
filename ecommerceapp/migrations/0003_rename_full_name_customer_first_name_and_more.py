# Generated by Django 4.1 on 2022-08-12 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0002_product_seller_alter_category_slug_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='full_name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='address',
            new_name='quater',
        ),
        migrations.AddField(
            model_name='customer',
            name='account_type',
            field=models.CharField(choices=[('buyer', 'Buyer'), ('seller', 'Seller')], default='buyer', max_length=256),
        ),
        migrations.AddField(
            model_name='customer',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='last_name',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='phone_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='region',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='store_address',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='town',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]

# Generated by Django 5.2.4 on 2025-07-24 08:46

import jdatetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام محصول')),
                ('quantity', models.PositiveIntegerField(verbose_name='تعداد')),
                ('expiration_date', models.DateField(default=jdatetime.date.today, verbose_name='تاریخ انقضا')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='تاریخ ثبت')),
            ],
            options={
                'verbose_name': 'محصول',
                'verbose_name_plural': 'محصولات',
            },
        ),
    ]

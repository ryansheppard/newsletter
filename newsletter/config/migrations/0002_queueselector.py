# Generated by Django 2.2.4 on 2019-08-02 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueueSelector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('queue_name', models.CharField(max_length=256)),
                ('selector_key', models.CharField(max_length=256)),
                ('selector_value', models.CharField(max_length=256)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

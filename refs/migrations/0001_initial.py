# Generated by Django 3.2.7 on 2021-11-02 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('explorer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MountPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_name', models.CharField(default='', max_length=255, verbose_name='ThrukHost host name')),
                ('description', models.CharField(max_length=255, verbose_name='Nagios Service name')),
                ('contragent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='explorer.contragent')),
                ('thruk_host', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='explorer.thrukhost')),
            ],
        ),
    ]

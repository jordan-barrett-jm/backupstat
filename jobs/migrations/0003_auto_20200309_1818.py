# Generated by Django 3.0.4 on 2020-03-09 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20200306_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupjob',
            name='comment',
            field=models.CharField(blank=True, default='', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='backupjob',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='backupjob',
            name='start_time',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='backupjob',
            name='status',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='backupjob',
            name='type',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]

# Generated by Django 5.1.7 on 2025-03-24 19:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EnvironmentalMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('pm25', models.FloatField(blank=True, help_text='Particulate matter 2.5 (μg/m³)', null=True, verbose_name='PM2.5')),
                ('pm10', models.FloatField(blank=True, help_text='Particulate matter 10 (μg/m³)', null=True, verbose_name='PM10')),
                ('o3', models.FloatField(blank=True, help_text='Ozone (ppb)', null=True, verbose_name='O3')),
                ('no2', models.FloatField(blank=True, help_text='Nitrogen dioxide (ppb)', null=True, verbose_name='NO2')),
                ('so2', models.FloatField(blank=True, help_text='Sulfur dioxide (ppb)', null=True, verbose_name='SO2')),
                ('co', models.FloatField(blank=True, help_text='Carbon monoxide (ppm)', null=True, verbose_name='CO')),
                ('temperature', models.FloatField(blank=True, help_text='Temperature (°C)', null=True)),
                ('humidity', models.FloatField(blank=True, help_text='Relative humidity (%)', null=True)),
                ('wind_speed', models.FloatField(blank=True, help_text='Wind speed (m/s)', null=True)),
                ('wind_direction', models.FloatField(blank=True, help_text='Wind direction (degrees)', null=True)),
                ('pressure', models.FloatField(blank=True, help_text='Atmospheric pressure (hPa)', null=True)),
                ('precipitation', models.FloatField(blank=True, help_text='Precipitation (mm)', null=True)),
                ('traffic_volume', models.IntegerField(blank=True, help_text='Number of vehicles', null=True)),
                ('traffic_speed', models.FloatField(blank=True, help_text='Average traffic speed (km/h)', null=True)),
                ('data_source', models.CharField(help_text='Source of the data (API name, sensor ID, etc.)', max_length=100)),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['timestamp'], name='api_environ_timesta_f8595f_idx'), models.Index(fields=['location'], name='api_environ_locatio_235cbc_idx')],
            },
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('target_time', models.DateTimeField(help_text='Time for which the prediction is made')),
                ('location', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('predicted_pm25', models.FloatField(blank=True, null=True, verbose_name='Predicted PM2.5')),
                ('predicted_pm10', models.FloatField(blank=True, null=True, verbose_name='Predicted PM10')),
                ('predicted_o3', models.FloatField(blank=True, null=True, verbose_name='Predicted O3')),
                ('predicted_no2', models.FloatField(blank=True, null=True, verbose_name='Predicted NO2')),
                ('predicted_traffic', models.IntegerField(blank=True, null=True, verbose_name='Predicted traffic volume')),
                ('model_name', models.CharField(help_text='Name of the prediction model used', max_length=100)),
                ('model_version', models.CharField(help_text='Version of the prediction model', max_length=50)),
                ('confidence', models.FloatField(blank=True, help_text='Prediction confidence (0-1)', null=True)),
            ],
            options={
                'ordering': ['-target_time'],
                'indexes': [models.Index(fields=['target_time'], name='api_predict_target__6282ae_idx'), models.Index(fields=['location'], name='api_predict_locatio_f4b677_idx')],
            },
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(max_length=255)),
                ('alert_type', models.CharField(choices=[('pollution', 'Pollution'), ('weather', 'Weather'), ('traffic', 'Traffic')], max_length=50)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('measurement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alerts', to='api.environmentalmeasurement')),
                ('prediction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alerts', to='api.prediction')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('alert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_alerts', to='api.alert')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-alert__timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='alert',
            index=models.Index(fields=['timestamp'], name='api_alert_timesta_5f3609_idx'),
        ),
        migrations.AddIndex(
            model_name='alert',
            index=models.Index(fields=['alert_type'], name='api_alert_alert_t_e1fa27_idx'),
        ),
        migrations.AddIndex(
            model_name='alert',
            index=models.Index(fields=['severity'], name='api_alert_severit_40581a_idx'),
        ),
        migrations.AddIndex(
            model_name='alert',
            index=models.Index(fields=['is_active'], name='api_alert_is_acti_2eb2b7_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='useralert',
            unique_together={('user', 'alert')},
        ),
    ]

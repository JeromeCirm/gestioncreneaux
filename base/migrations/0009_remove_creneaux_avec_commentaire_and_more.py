# Generated by Django 4.0 on 2024-08-28 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_utilisateur_information'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creneaux',
            name='avec_commentaire',
        ),
        migrations.RemoveField(
            model_name='creneaux',
            name='avec_inscription',
        ),
        migrations.AddField(
            model_name='creneaux',
            name='lien',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='creneaux',
            name='type_creneau',
            field=models.IntegerField(default=0),
        ),
    ]
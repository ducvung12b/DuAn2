# Generated by Django 5.1 on 2024-09-18 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_likedrecipe'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LikedRecipe',
        ),
    ]

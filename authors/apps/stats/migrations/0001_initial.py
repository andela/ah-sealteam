from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('articles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReadingStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_last_at', models.DateTimeField(auto_now=True)),
                ('no_read', models.PositiveIntegerField(default=1)),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='article_read', to='articles.Article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_reader', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-read_last_at',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='readingstatistics',
            unique_together={('article', 'user')},
        ),
    ]

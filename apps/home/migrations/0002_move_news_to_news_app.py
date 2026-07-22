from django.db import migrations


class Migration(migrations.Migration):
    """Companion to apps/news/migrations/0001_initial.py.

    State-only: removes ``News`` from apps.home's migration state. The
    ``home_news`` database table is left completely untouched — it is
    now owned (and read via the same table, per ``Meta.db_table``) by
    ``apps.news.models.News`` instead.
    """

    dependencies = [
        ("home", "0001_initial"),
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="News"),
            ],
        ),
    ]

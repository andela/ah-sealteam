python manage.py makemigrations authentication
python manage.py makemigrations profiles
psql $DATABASE_URL -c "DELETE FROM django_migrations WHERE app='articles';"
python manage.py makemigrations articles
python manage.py makemigrations
python manage.py migrate --fake

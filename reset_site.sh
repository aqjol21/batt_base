rm -rf migrations
rm app.db
flask db init
flask db migrate
flask db upgrade

python -m db_init
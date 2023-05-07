#!/bin/sh

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for MySQL..."

    while ! mysql -h "$SQL_HOST" -u "$SQL_USER" -p"$SQL_PASSWORD" -e 'SELECT 1' > /dev/null; do
      echo "MySQL is unavailable - sleeping"
      sleep 1
    done
    # Somente na primeira vez, para construção do banco de dados
    # rm -rf migrations
    # flask db init && flask db migrate -m 'Initial migration' && flask db upgrade
    echo "MySQL started"
fi

exec "$@"

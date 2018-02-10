sudo -u postgres psql -c 'CREATE DATABASE cutrect_prod;'
sudo -u postgres psql -c "CREATE USER lqzj WITH PASSWORD 'lqdzjsql';"
sudo -u postgres psql -c "ALTER USER lqzj superuser createrole createdb replication;"
sudo -u postgres psql -c "ALTER ROLE lqzj SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE lqzj SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE lqzj SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cutrect_prod TO lqzj;"

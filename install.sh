#!/bin/bash

# install script for caves

#settings

INSTALLDIR="/var/www"
APACHEDIR="/etc/apache2"

echo "Checking dependencies"

# check for python
PYVERSION=$(python --version 2>&1)
PYVERSIONMAJ=$(python --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1)
if [ "$PYVERSIONMAJ" -eq "2" ]
then
    echo $PYVERSION "ok"
else
    echo "Python 2 not found"
    exit
fi

# check for python libraries

# flask
FLASK=$(python -c "import flask; print flask.__version__" 2>&1)
if [ $? -eq 0 ]
then
    echo "Python Flask" $FLASK "ok"
else
    apt install -y python-flask
fi

# bitarray
BITARRAY=$(python -c "import bitarray; print bitarray.__version__" 2>&1)
if [ $? -eq 0 ]
then
    echo "Python Bitarray" $BITARRAY "ok"
else
    apt install -y python-bitarray
fi

# openssl
OPENSSL=$(command -v openssl)
if [ $? -eq 0 ]
then
    echo "OPENSSL ok"
else
    apt install -y openssl
fi
# openssl python library
PYOPENSSL=$(python -c "import OpenSSL; print OpenSSL.__version__" 2>&1)
if [ $? -eq 0 ]
then
    echo "Python OpenSSL" $PYOPENSSL "ok"
else
    apt install -y python-openssl
fi
# mysql
MYSQL=$(command -v mysql)
if [ $? -eq 0 ]
then
    echo $(mysql --version) "ok"
else
    apt install -y mysql-server
fi
MYSQLDB=$(python -c "import MySQLdb; print MySQLdb.__version__" 2>&1)
if [ $? -eq 0 ]
then
    echo "Python MySQLdb" $MYSQLDB "ok"
else
    apt install -y python-mysqldb
fi

# apache
APACHE=$(command -v apache2)
if [ $? -eq 0 ]
then
    APACHE=$(apache2 -v | head -n1)
    echo "Apache" $APACHE "ok"
else
    apt install -y apache2
fi

# apache mod_wsgi
WSGI=$(a2enmod wsgi > /dev/null 2>&1)
if [ $? -eq 0 ]
then
    echo "Apache mod_wsgi" "ok"
else
    apt install -y libapache2-mod-wsgi
fi

echo "Dependencies" "ok"

echo "Setting up database for caves"
# mysql database creation for Caves
printf "\tDatabase Name: Caves\n"
#read DATABASE, database name is hardwired
DATABASE="caves"
printf "\tUser: "
read USER
if [ "$USER" = "" ]
then
    USER="caves"
fi
printf "\tPassword: "
read PASSWORD
while [ "$PASSWORD" = "" ]
do
    printf "\tPassword: "
    read PASSWORD
done
printf "\tHost: "
read HOST
if [ "$HOST" = "" ]
then
    HOST="localhost"
fi

# echo "CREATE DATABASE $DATABASE;"
echo "CREATE USER \"$USER\"@\"$HOST\" IDENTIFIED BY \"$PASSWORD\";" >> Caves/NewCred/sqlinit.sql
echo "" >> Caves/NewCred/sqlinit.sql
echo "GRANT ALL PRIVILEGES on $DATABASE.* TO \"$USER\"@\"$HOST\";" >> Caves/NewCred/sqlinit.sql

echo "Running: mysql -u root -p < Caves/NewCred/sqlinit.sql"
mysql -u root -p < Caves/NewCred/sqlinit.sql

#copying files to INSTALLDIR
printf "copying files to $INSTALLDIR"
mkdir "$INSTALLDIR/Caves"
cp -r Caves/Caves $INSTALLDIR/Caves
cp Caves/caves.* $INSTALLDIR/Caves
cp Caves/Caves.conf $INSTALLDIR/Caves
printf "ok\n"

# editing database settings files for caves
sed -i "s/__user__/$USER/g" $INSTALLDIR/Caves/Caves/dbsettings.py
sed -i "s/__host__/$HOST/g" $INSTALLDIR/Caves/Caves/dbsettings.py
sed -i "s/__password__/$PASSWORD/g" $INSTALLDIR/Caves/Caves/dbsettings.py
sed -i "s/__database__/$DATABASE/g" $INSTALLDIR/Caves/Caves/dbsettings.py

# copying Apache config file for caves
printf "Copying Apache config file for caves to $APACHEDIR/sites-available"
cp $INSTALLDIR/Caves/Caves.conf $APACHEDIR/sites-available
printf " ok\n"

printf "Enabling Apache site"
a2ensite Caves.conf > /dev/null 2>&1
printf " ok\n"

printf "Restarting Apache server"
service apache2 stop > /dev/null 2>&1
service apache2 start > /dev/null 2>&1
printf " ok\n"
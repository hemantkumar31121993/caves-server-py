#!/bin/bash

# install script for caves

#settings

INSTALLDIR="/var/www"
APACHEDIR="/etc/apache2"

pritty() {
    l=$(echo $1 | wc -c)
    l=$(expr 60 - $l) 
    printf "%s \33[1;32m%${l}s\33[m\n" "$1" "[$2]"
}

echo "Checking dependencies"

# check for python
PYVERSION=$(python --version 2>&1)
PYVERSIONMAJ=$(python --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1)
if [ "$PYVERSIONMAJ" -eq "2" ]
then
    pritty "$PYVERSION" "OK"
else
    echo "Python 2 not found. Please install Python 2."
    exit
fi

# check for python libraries

# flask
FLASK=$(python -c "import flask; print flask.__version__" 2>&1)
if [ $? -eq 0 ]
then
    pritty "Python Flask $FLASK" "OK"
else
    apt install -y python-flask -qq > /dev/null 2>&1
    pritty "Python Flask $FLASK" "OK"
fi

# bitarray
BITARRAY=$(python -c "import bitarray; print bitarray.__version__" 2>&1)
if [ $? -eq 0 ]
then
    pritty "Python Bitarray $BITARRAY" "OK"
else
    apt install -y python-bitarray -qq > /dev/null 2>&1
    pritty "Python Bitarray $BITARRAY" "OK"
fi

# openssl
OPENSSL=$(command -v openssl)
if [ $? -eq 0 ]
then
    pritty "$(openssl version | xargs)" "OK"
else
    apt install -y openssl -qq > /dev/null 2>&1
    pritty "$(openssl version | xargs)" "OK"
fi
# openssl python library
PYOPENSSL=$(python -c "import OpenSSL; print OpenSSL.__version__" 2>&1)
if [ $? -eq 0 ]
then
    pritty "Python OpenSSL $PYOPENSSL" "OK"
else
    apt install -y python-openssl -qq > /dev/null 2>&1
    pritty "Python OpenSSL $PYOPENSSL" "OK"
fi

# mysql
MYSQL=$(command -v mysql)
if [ $? -eq 0 ]
then
    pritty "$(mysql --version | cut -d ',' -f 1 | xargs)" "OK"
else
    apt install -y mysql-server -qq > /dev/null 2>&1
    pritty "$(mysql --version | cut -d ',' -f 1 | xargs)" "OK"
fi
MYSQLDB=$(python -c "import MySQLdb; print MySQLdb.__version__" 2>&1)
if [ $? -eq 0 ]
then
    pritty "Python MySQLdb $MYSQLDB" "OK"
else
    apt install -y python-mysqldb -qq > /dev/null 2>&1
    pritty "Python MySQLdb $MYSQLDB" "OK"
fi

# apache
APACHE=$(command -v apache2)
if [ $? -eq 0 ]
then
    APACHE=$(apache2 -v | head -n1)
    pritty "Apache $APACHE" "OK"
else
    apt install -y apache2 -qq > /dev/null 2>&1
    pritty "Apache $APACHE" "OK"
fi

# apache mod_wsgi
WSGI=$(a2enmod wsgi > /dev/null 2>&1)
if [ $? -eq 0 ]
then
    pritty "Apache mod_wsgi" "OK"
else
    apt install -y libapache2-mod-wsgi -qq > /dev/null 2>&1
    pritty "Apache mod_wsgi" "OK"
fi

pritty "Dependencies" "OK"

echo ""
echo ""
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
echo "Appending following to Caves/NewCred/sqlinit.sql"
printf "\tCREATE USER \"$USER\"@\"$HOST\" IDENTIFIED BY \"$PASSWORD\";\n"
printf "\tGRANT ALL PRIVILEGES on $DATABASE.* TO \"$USER\"@\"$HOST\";\n"
echo "CREATE USER \"$USER\"@\"$HOST\" IDENTIFIED BY \"$PASSWORD\";" >> Caves/NewCred/sqlinit.sql
echo "" >> Caves/NewCred/sqlinit.sql
echo "GRANT ALL PRIVILEGES on $DATABASE.* TO \"$USER\"@\"$HOST\";" >> Caves/NewCred/sqlinit.sql

echo "Running: mysql -u root -p < Caves/NewCred/sqlinit.sql"
echo "Enter root password for MySQL when prompted"
mysql -u root -p < Caves/NewCred/sqlinit.sql

pritty "Populating database" "DONE"

#copying files to INSTALLDIR
printf "Copying files to $INSTALLDIR\n"
mkdir "$INSTALLDIR/Caves"
cp -r Caves/Caves $INSTALLDIR/Caves
cp Caves/caves.* $INSTALLDIR/Caves
cp Caves/Caves.conf $INSTALLDIR/Caves
pritty "Copying files to $INSTALLDIR" "OK"

# editing database settings files for caves
sed -i "s/__user__/$USER/g" $INSTALLDIR/Caves/Caves/dbsettings.py
sed -i "s/__host__/$HOST/g" $INSTALLDIR/Caves/Caves/dbsettings.py
sed -i "s/__password__/$PASSWORD/g" $INSTALLDIR/Caves/Caves/dbsettings.py
sed -i "s/__database__/$DATABASE/g" $INSTALLDIR/Caves/Caves/dbsettings.py

# copying Apache config file for caves
printf "Copying Apache config file for caves to $APACHEDIR/sites-available\n"
cp $INSTALLDIR/Caves/Caves.conf $APACHEDIR/sites-available
pritty "Copying Apache config file" "DONE"

printf "Enabling Apache site\n"
a2ensite Caves.conf > /dev/null 2>&1
pritty "Enabling Apache site" "DONE"

printf "Restarting Apache server\n"
service apache2 stop > /dev/null 2>&1
service apache2 start > /dev/null 2>&1
pritty "Restarting Apache server" "DONE"
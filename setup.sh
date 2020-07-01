#!/usr/bin/env bash
# Author: Bahawal Waraich

DB=""
SETTINGS=""

DEPENDENCIES="python-pip sqlite3 python-flask python-passlib"
SERVER="server_base.py"
NEW_SERVER="server.py"
SCHEMA="schema.sql"
PRIVKEY='privateKey.key'
CERT='certificate.crt'

ACTIVE_USER=`logname`
R=`tput setaf 1`						
G=`tput setaf 2`						
RC=`tput sgr0`							

function displayHelp() {
	cat <<EOF
usage:
	$0 -d DB -c CONFIGURATION
parameters:
	-d
		Specify a DB file that will be created to use the server.
		Example: '/tmp/ctf.db'
	-c
		Specify the configuration file that will be used the server.
		Example: 'linux_basic.json'
	-h
		Display help text
EOF
}


function installDependencies(){

	echo "$0: ${G}Dependenices being installed...${RC}"
	apt-get update || panic
	apt-get -y install $DEPENDENCIES || panic
}

function createCert(){

	echo "$0: ${G}HTTPS certificates being created...${RC}"
	openssl req -newkey rsa:2048 -nodes -keyout "$PRIVKEY" \
							-x509 -days 365 -out "$CERT" <<EOF || panic
GB
England
London
Swansea University
880114
Bahawal Waraich
bahawal@hotmail.co.uk
EOF

	sed "0,/\$CERT/{s/\$CERT/$CERT/}" $SERVER > $NEW_SERVER || panic
	sed -i "0,/\$PRIVKEY/{s/\$PRIVKEY/$PRIVKEY/}" $NEW_SERVER || panic
	

}

function createDatabase(){

	echo "$0: ${G}Sqlite3 DB being created...${RC}"

	rm -f $DB
	sqlite3 $DB < $SCHEMA || panic
	chown $ACTIVE_USER $DB
	sed -i '0,/\$DB/{s/\$DB/'${DB//\//\\/}'/}' $NEW_SERVER  || panic

}

function configureCTF(){

	echo "$0: ${G}CTF being configured...${RC}"

	sed -i "0,/\$SETTINGS/{s/\$SETTINGS/$SETTINGS/}" $NEW_SERVER || panic

}

function createNewServer(){

	cp $SERVER $NEW_SERVER
	chown $ACTIVE_USER $NEW_SERVER
	chmod 744 $NEW_SERVER
}

function configureFirewall(){
	
	echo "$0: ${G}Firewall for HTTPS connections being configured...${RC}"
	ufw allow https
}

function main()
{

	installDependencies

	createNewServer

	createCert
	
	createDatabase

	configureCTF

	configureFirewall

	echo "$0: ${G}Successfully setup CTF server!${RC}"
	echo "$0: ${G} You can now run the server with the command: ${RC}"
	echo '`sudo python3 server.py`'

	exit 0
	
}

function panic
{
	echo "$0: ${R}fatal error${RC}"
	exit -1
}


if [ "$(id -u)" != "0" ]; then
	echo "$0: ${R}you must be root to configure this box.${RC}"
	exit -1
fi

while getopts d:c:h opt; do

	case $opt in
		d)
			echo "$0: ${G}the following DB file is being used: ${OPTARG}${RC}"
			DB=$OPTARG
			;;
		c)
			echo "$0: ${G}the following configuration file is being used: ${OPTARG}${RC}"
			SETTINGS=$OPTARG
			;;
		h)
			displayHelp
			exit 0
			;;
		\?)
			exit -1
			;;
	esac
done


if [ "$DB" == "" ]; then
	echo "$0: ${R}you must specify a DB file!${RC}"
	displayHelp
	exit -1
fi

if [ "$SETTINGS" == "" ]; then
	echo "$0: ${R}you must specify a configuration file!${RC}"
	displayHelp
	exit -1
fi

main "$@"

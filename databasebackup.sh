#!/bin/bash

# title           - databasebackup.sh
# description     - This script takes the backup of MySQL database and also check for number of backups to be retained.
# author					- Aniruddha Biyani
# date            - 20150816
# version         - v1
# usage		 				- bash databasebackup.sh

####################### Set these variables appropriately ###########################
# port="3306"															# Port number on which MySQL is running.
# username="root";                        # MySQL username
# password="";			                      # MySQL password
# retain=3																# Number of backups that you want to retain.

# IMPORTANT: Please make sure the directories exist and have correct permissions before running the script.
# backupdir=          										# Path to the directory where the backups will be created.
# log=         														# Path to the directory where the log file will be created.
# filename=mysql-backup-$(date +%F).sql;	# The filename of the backup file.
#####################################################################################

starttime=`date +%s`;

# Checking if the directory exists and we can write into that directory.
echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | INFO | Checking for the prerequisite" >> $log;
if [ -d "$backupdir" ];
then
	touch "$backupdir/testfile"
	if [ $? -ne 0 ];
	then
		echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | ERROR | The directory is not writable"  >> $log;
		exit 1;
	else
		continue;
	fi
	rm "$backupdir/testfile"
fi

if [ -w "$log" ];
then
	:
else
	echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | INFO | The log file is not writable" >> $log;
	exit 1;
fi

# Check if we can connect to the database with the credentials given above.
mysqlcheck=$(mysql -u$username -p$password -P $port -e "SHOW VARIABLES LIKE '%version%';" || echo 0);

echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $myname | INFO | Looking for files older than $retain days."  >> $log;
if [ $(ls $backupdir/cloudera-mysql-* -1 | wc -l) -gt $retain ]; then
	echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $myname | INFO | Found backup(s) older than $retain days."  >> $log;
	count=0;
	ls $backupdir/cloudera-mysql-* -r1 |
	while read -r LINE; do
		if [ $count -gt $((retain-1)) ]; then
			echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $myname | INFO | Deleting file $LINE."  >> $log;
			rm $LINE;
		fi
		count=$((count+1));
	done;
else
	echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $myname | INFO | Could not find any backups older than $retain days."  >> $log;
fi

# If mysqlcheck is 0, that means we cannot connect to the database with the credentials given above. We'll make a log entry and exit. Else, we will make a mysqldump
if [ "$mysqlcheck" == 0 ]; then
	echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | FATAL | Could not connect to database '$database' on after 3 retries." >> $log;
	echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | INFO | One of the check for prerequisite failed." >> $log;
	exit 1;
else
	echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | INFO | STARTED: Backup of database has started." >> $log;
	mysqldump -u$username -p$password -P $port -q --all-databases --max-allowed-packet=1G > $backupdir/$filename;
	if [ $? -eq 0 ];
	then
		echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | INFO | DONE: Backup completed."  >> $log;
	else
		echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | ERROR | FAILED: Backup of databases failed." >> $log;
		exit 1;
	fi
fi

endtime=`date +%s`;
runtime=$((endtime - starttime));

echo -e "$(date +%Y/%m/%d\ %H:%M:%S) | $hostname | INFO | SCRIPT COMPLETED IN $(($runtime/3600)) HRS, $((($runtime/60)%60)) MIN AND $(($runtime%60)) SECS." >> $log;

#!/bin/bash


while [ $# -gt 0 ]; do
        case $1 in
                -c)
                        CONFIG_FILE_PATH="$2"
                        shift 2
                        ;;
                *)
                        ${ECHO} "Unknown Option \"$1\"" 1>&2
                        exit 2
                        ;;
        esac
done
 
if [ -z $CONFIG_FILE_PATH ] ; then
        SCRIPTPATH=$(cd ${0%/*} && pwd -P)
        CONFIG_FILE_PATH="${SCRIPTPATH}/pg_backup.config"
fi
 
if [ ! -r ${CONFIG_FILE_PATH} ] ; then
        echo "Could not load config file from ${CONFIG_FILE_PATH}" 1>&2
        exit 1
fi
 
source "${CONFIG_FILE_PATH}"
SUFFIX="-daily"
FINAL_BACKUP_DIR=$BACKUP_DIR"`date +\%Y-\%m-\%d`$SUFFIX/"
echo $FINAL_BACKUP_DIR
SUFFIX2=$SUFFIX".tar.gz"
ARCHIVE="`date +\%Y-\%m-\%d`$SUFFIX2"
tar -zcvf $BACKUP_DIR$ARCHIVE $FINAL_BACKUP_DIR

# use ssh private and publish keys move the files- eliminates the need to passwords. 
scp -i /home/j9/.ssh/id_rsa $BACKUP_DIR$ARCHIVE "pgbackups@162.243.137.94:/home/pgbackups/data_monitoring_backups"
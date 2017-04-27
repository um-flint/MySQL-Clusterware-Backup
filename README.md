This code acts as a wrapper for scheduling backup jobs for MySQL instances that are running on top of Oracle Clusterware with MySQL Enterprise Backup.

By scheduling this as a cron job on every node in the cluster, you can make sure the databases are backed up from the currently active node only.

Currently, this code assumes:
 * You are using Oracle Secure Backup to write to tapes as your backup target.
 * The socket is located in the datadir of the instance and named mysql.sock
 * You have configured a local account to run this job that has permission to log in to the MySQL database using auth_socket
 * You have a copy of MySQL Enterprise Backup located inside the MYSQL_HOME in a directory named 'meb'
 * You are not using MySQL that was installed from a package (i.e. you are using the tar version)
 * You are using Python 2.7

If you are using a distribution that includes an older version of Python (such as Oracle Linux 6) you will need to install Python 2.7 from Software Collections.

You need to copy the sample config to a file named mysqlClusterwareBackup.cfg and tweak it to your environment.  The config file needs to be in the same directory as the script.

It has been tested with:
 * Oracle Linux 6
 * MySQL 5.6 and 5.7
 * MySQL Enterprise Backup 3.12.3 and 4.1.0
 * Oracle Grid Infrastructure/Clusterware 12.1.0.2
 * Oracle Grid Infrastructure Standalone Agent 7.1.0


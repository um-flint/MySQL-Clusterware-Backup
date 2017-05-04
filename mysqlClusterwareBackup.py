#!/usr/bin/python

import ConfigParser
import subprocess
import socket
import time
import shutil
import os
import sys
import glob

def main():
    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.join(sys.path[0], 'mysqlClusterwareBackup.cfg')))

    xag_home = config.get('clusterware','xag_home')
    grid_home = config.get('clusterware','grid_home')
    instances = config.get('clusterware', 'instances')

    agctl = xag_home + '/bin/agctl'
    hostname = socket.gethostname().split('.')[0]

    for instance in instances.split(','):
        instance_name = instance.strip()
        
        xag_status = subprocess.check_output([agctl, 'status', 'mysql_server', instance_name]).strip()

        if 'is running on' in xag_status:
            if hostname in xag_status:
                print 'Instance', instance_name, 'is running on this node - continuing'
                instance_config = subprocess.check_output([agctl, 'config', 'mysql_server', instance_name]).strip()

                for line in instance_config.split('\n'):
                    if line.startswith('Mysql home:'):
                        mysql_home = line.split(':')[1].strip()

                    if line.startswith('Datadir:'):
                        datadir = line.split(':')[1].strip()

                if mysql_home is None:
                    print '  Could not find MySQL Home for', instance_name, '- skipping it'

                elif datadir is None:
                    print '  Could not find MySQL Home for', instance_name, '- skipping it'

                else:
                    print '  Attempting to backup instance', instance_name

                    mysql_socket = datadir + '/mysql.sock'
                    use_osb = config.getboolean('mysqlbackup', 'use_osb')
                    backup_dir = mysql_home + '/' + config.get('mysqlbackup', 'backup-dir')
                    backup_user = config.get('mysqlbackup', 'user')
                    verbose_output = config.getboolean('mysqlbackup', 'verbose')
                    use_compression = config.getboolean('mysqlbackup','compression')
                    
                    meb = mysql_home + '/meb/mysqlbackup'
                    socket_arg = '--socket='+mysql_socket
                    user_arg = '--user='+backup_user
                    bdir_arg = '--backup-dir='+backup_dir
                    
                    meb_cmd = []
                    meb_cmd.extend([meb, socket_arg, user_arg, bdir_arg])

                    if use_compression is True:
                        meb_cmd.append('--compress')

                        if config.has_option('mysqlbackup', 'compression_method'):
                            compression_type = '--compress-method=' + config.get('mysqlbackup', 'compression_method')
                            meb_cmd.append(compression_type)

                    if use_osb is True:
                        sbt_db = config.get('mysqlbackup', 'sbt-database-name')

                        bi_arg = '--backup-image=sbt:'+instance_name+'-'+time.strftime('%Y-%m-%d')
                        sbt_db_arg = '--sbt-database-name='+sbt_db
                        btype_arg = 'backup-to-image'
                       
                        meb_cmd.extend([bi_arg, sbt_db_arg, btype_arg])
                        try: 
                            backup_run = subprocess.check_output(meb_cmd, stderr=subprocess.STDOUT).strip()
                            print '  mysqlbackup return code was 0 - backup appears to have succeeded'
                            if verbose_output is True:
                                print '  verbose output enabled - output from mysqlbackup follows'
                                print '**************************************************************'
                                print backup_run
                                print '**************************************************************'
                            else:
                                if backup_run.endswith('mysqlbackup completed OK!'):
                                    print '  last line of output was "mysqlbackup completed OK!" - success!'
                                else:
                                    print '  unable to verify backup was successful - output from mysqlbackup follows'
                                    print '**************************************************************'
                                    print backup_run
                                    print '**************************************************************'

                        except subprocess.CalledProcessError as e:
                            print '  mysqlbackup return code was', e.returncode, '- backup failed'
                            print '  The output from mysqlbackup follows'
                            print '**************************************************************'
                            print e.output.strip()
                            print '**************************************************************'

                        if config.has_option('mysqlbackup', 'log-dir'):
                            meb_log_dir = mysql_home + '/' + config.get('mysqlbackup', 'log-dir')
                            meb_src_log = backup_dir + '/meta/MEB*.log'
                            print '  copying MEB log to', meb_log_dir
                            for data in glob.glob(meb_src_log):
                                shutil.copy(data, meb_log_dir)

                        print '  removing',  backup_dir
                        shutil.rmtree(backup_dir)

                    else:
                        print '  Backups not using Oracle Secure Backup not implemented yet - skipping'

            else:
                print 'Instance', instance_name, 'is not running on this node - skipping it'
        elif 'is not running' in xag_status:
            print 'Instance', instance_name, 'is  not running at all - skipping it'

        else:
            print 'Instance', instance_name, 'appears to have an unusual status - skipping and displaying output from agctl'
            print ' ', xag_status
        print
        
    return

if __name__ == '__main__':
    main()

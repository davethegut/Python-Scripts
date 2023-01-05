#!/usr/bin/env python3
###############################################
# David Elgut david.elgut@graylog.com
# Evan Tepsic 

# Last modified 1/5/2023
# Version 2022-12-27
###############################################

################################################
#		MONGO INSTALL
################################################

import subprocess
import shutil
import re

"""
# Import the public key used by the package management system
subprocess.run(["sudo", "apt-key", "adv", "--keyserver", "hkp://keyserver.ubuntu.com:80", "--recv", "9DA31620334BD75D9DCB49F368818C72E52529D4"])

# Create a list file for MongoDB
subprocess.run(["echo", "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse", "|", "sudo", "tee", "/etc/apt/sources.list.d/mongodb-org-5.0.list"])

# Reload the package database
subprocess.run(["sudo", "apt-get", "update"])

# Install the MongoDB package
subprocess.run(["sudo", "apt-get", "install", "-y", "mongodb"])

# Start the MongoDB service
subprocess.run(["systemctl", "start", "mongodb"])

#reload the daemon
subprocess.run(["sudo", "systemctl", "daemon-reload"])

# Enable the MongoDB service to start on boot
subprocess.run(["systemctl", "enable", "mongodb.service"])

#restart MongoDB service and check if it is running properly
subprocess.run(["sudo", "systemctl", "restart", "mongodb.service"])
subprocess.run(["sudo", "systemctl", "status", "mongodb"])
"""
################################################
#		OPENSEARCH INSTALL
################################################

with open("/etc/systemd/system/disable-transparent-huge-pages.service", "w") as f:
  f.write("""
Description=Disable Transparent Huge Pages (THP)
DefaultDependencies=no
After=sysinit.target local-fs.target
[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo never | tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null'
[Install]
WantedBy=basic.target
""")
subprocess.run(["sudo", "systemctl", "daemon-reload"])
subprocess.run(["sudo", "systemctl", "enable", "disable-transparent-huge-pages.service"])
subprocess.run(["sudo", "systemctl", "start", "disable-transparent-huge-pages.service"])

  # Create OpenSearch user
subprocess.run(["sudo", "adduser", "--system", "--disabled-password", "--disabled-login", "--home", "/var/empty", "--no-create-home", "--quiet", "--force-badname", "--group", "opensearch"])

# Download and install OpenSearch
subprocess.run(["wget", "https://artifacts.opensearch.org/releases/bundle/opensearch/2.0.1/opensearch-2.0.1-linux-x64.tar.gz"])
subprocess.run(["sudo", "tar", "-zxf", "opensearch-2.0.1-linux-x64.tar.gz"])
subprocess.run(["sudo", "mv", "opensearch-2.0.1", "opensearch"])
subprocess.run(["sudo", "mkdir", "/graylog"])
subprocess.run(["sudo", "mv", "opensearch", "/graylog"])
subprocess.run(["sudo", "mkdir", "/var/log/opensearch"])
subprocess.run(["sudo", "mkdir", "/graylog/opensearch/data"])
subprocess.run(["sudo", "chown", "-R", "opensearch:opensearch", "/graylog/opensearch/"])
subprocess.run(["sudo", "chown", "-R", "opensearch:opensearch", "/var/log/opensearch"])
subprocess.run(["sudo", "chmod", "-R", "2750", "/graylog/opensearch/"])
subprocess.run(["sudo", "chmod", "-R", "2750", "/var/log/opensearch"])
subprocess.run(["sudo", "-u", "opensearch", "touch", "/var/log/opensearch/graylog.log"])

# Create OpenSearch system service
with open("/etc/systemd/system/opensearch.service", "w") as f:
  f.write("""
[Unit]
Description=Opensearch
Documentation=https://opensearch.org/docs/latest
Requires=network.target remote-fs.target
After=network.target remote-fs.target
ConditionPathExists=/graylog/opensearch
ConditionPathExists=/graylog/opensearch/data
[Service]
Environment=OPENSEARCH_HOME=/graylog/opensearch
Environment=OPENSEARCH_PATH_CONF=/graylog/opensearch/config
ReadWritePaths=/var/log/opensearch
User=opensearch
Group=opensearch
WorkingDirectory=/graylog/opensearch
ExecStart=/graylog/opensearch/bin/opensearch
# Specifies the maximum file descriptor number that can be opened by this process
LimitNOFILE=65535
# Specifies the maximum number of processes
LimitNPROC=4096
# Specifies the maximum size of virtual memory
LimitAS=infinity
# Specifies the maximum file size
LimitFSIZE=infinity
# Disable timeout logic and wait until process is stopped
TimeoutStopSec=0
# SIGTERM signal is used to stop the Java process
KillSignal=SIGTERM
# Send the signal only to the JVM rather than its control group
KillMode=process
# Java process is never killed
SendSIGKILL=no
# When a JVM receives a SIGTERM signal it exits with code 143
SuccessExitStatus=143
# Allow a slow startup before the systemd notifier module kicks in to extend the timeout
TimeoutStartSec=180
[Install]
WantedBy=multi-user.target
""")

################################################
#		OPENSEARCH CONFIGURATIONS
################################################
  # Graylog Configuration for OpenSearch
subprocess.run(["sudo", "mkdir", "/graylog/opensearch/config"])
with open("/graylog/opensearch/config/opensearch.yml", "w") as f:
  f.write("""
cluster.name: graylog
node.name: localhost
path.data: /graylog/opensearch/data
path.logs: /var/log/opensearch
network.host: localhost
#discovery.seed_hosts: ["SERVERNAME01", "SERVERNAME02", "SERVERNAME03"]
#cluster.initial_master_nodes: ["SERVERNAME01", "SERVERNAME02", "SERVERNAME03"]
action.auto_create_index: false
plugins.security.disabled: true
discovery.type: single-node
""")

# Enable JVM options
subprocess.run(["sudo", "touch", "/graylog/opensearch/config/jvm.options"])
  
# Configure kernel parameters at runtime
subprocess.run(["sudo", "sysctl", "-w", "vm.max_map_count=262144"])
subprocess.run(["sudo", "echo", "'vm.max_map_count=262144'", ">>", "/etc/sysctl.conf"])

# Finally, enable the system service
subprocess.run(["sudo", "systemctl", "daemon-reload"])
subprocess.run(["sudo", "systemctl", "enable", "opensearch.service"])
subprocess.run(["sudo", "systemctl", "start", "opensearch.service"])

################################################
#		GRAYLOG INSTALL
################################################

# Download the repository package
subprocess.run(["wget", "https://packages.graylog2.org/repo/packages/graylog-5.0-repository_latest.deb"])

# Install the repository package
subprocess.run(["sudo", "dpkg", "-i", "graylog-5.0-repository_latest.deb"])

# Update the package list and install Graylog Enterprise
subprocess.run(["sudo", "apt-get", "update"])
subprocess.run(["sudo", "apt-get", "install", "graylog-enterprise"])


# Get the Graylog configuration values from the user
graylog_bind_address = input('Enter the bind address for the Graylog server (e.g. 0.0.0.0:9000): ')
graylog_admin_password = input('Enter the password for the admin user: ')

# Install pwgen
subprocess.run(["sudo", "apt", "install", "pwgen", "-y"])

# Create the hash password for passwords_secret in graylog.conf file
password_secret = subprocess.check_output(["pwgen", "-N", "1", "-s", "96"])
password_secret_output = password_secret.decode('utf-8').strip()

# Create the hash password for root_password_sha2 in graylog.conf file
root_password = subprocess.check_output(["echo", "-n", graylog_admin_password, "|", "shasum", "-a", "256"])
root_password_output = root_password.decode('utf-8').strip()

# Uncomment the http_bind_address line in the configuration file
subprocess.run(["sudo", "sed", "-i", "-e", "105,105 s/#http_bind_address/http_bind_address/'", "/etc/graylog/server/server.conf"])

# Append the Graylog configuration values to the end of the file
subprocess.run(["sudo", "sed", "-i", "/http_bind_address = .*/http_bind_address = " + graylog_bind_address + "/g", "/etc/graylog/server/server.conf"])
subprocess.run(["sudo", "sed", "-is/password_secret = .*/password_secret = " + password_secret_output + "/g", "/etc/graylog/server/server.conf"])
subprocess.run(["sudo", "sed", "-is/root_password_sha2 = .*/root_password_sha2 = " + root_password_output + "/g", "/etc/graylog/server/server.conf"])

# Reload the daemon and enable the Graylog Enterprise service
subprocess.run(["sudo", "systemctl", "daemon-reload"])
subprocess.run(["sudo", "systemctl", "enable", "graylog-server.service"])

# Start the Graylog Enterprise service
subprocess.run(["sudo", "systemctl", "start", "graylog-server.service"])

# List all active services and grep for Graylog
# subprocess.run(["sudo", "systemctl", "--type=service", "--state=active", "|", "grep", "graylog"])
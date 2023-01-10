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
import hashlib
import shutil
import re


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

###############################################################
# This is the section of the graylog configuration process
# Where we are using an input statement to write to the 
# server.conf file and substituting it after the first 
# "#http_bind_address" to use as the bind address
# for when the user uses graylog 
###############################################################

# Open the server.conf file in read mode
with open('/etc/graylog/server/server.conf', 'r') as f:
    lines = f.readlines()

# Find the line with "#http_bind_address = " and store its index
index = -1
for i, line in enumerate(lines):
    if line.startswith('#http_bind_address = '):
        index = i
        break

# Uncomment the line with "#http_bind_address = "
lines[index] = lines[index].lstrip('#')

# Prompt the user for input and store it in a variable
graylog_bind_address = input('Enter the bind address for the Graylog server (e.g. 0.0.0.0:9000): ')

# Insert the user input after the line with "http_bind_address = "
parts = lines[index].split('=')
parts[1] = f' {graylog_bind_address}\n'
lines[index] = '='.join(parts)


# Open the file in write mode and overwrite it with the modified lines
with open('/etc/graylog/server/server.conf', 'w') as f:
    f.writelines(lines)
    
###############################################################
# This is the section for generating the hashed passwords
# Based on the user input, and then writing it back to the 
# server.conf file.
###############################################################
  
# Install pwgen for creating the hash
subprocess.run(["sudo", "apt", "install", "pwgen", "-y"])

# Here we will be creating and writing the first inital hash 
# for the variable "password_secret=" in the graylog.conf file
# Open the file in read mode
with open('/etc/graylog/server/server.conf', 'r') as conf_file:
    conf_lines = conf_file.readlines()

# Find the line with "password_secret =" and store its index
pw_index = -1
for l, line in enumerate(conf_lines):
    if line.startswith('password_secret ='):
        pw_index = l
        break

# Generate a 96-character long password
new_password = subprocess.run(["pwgen", "-N", "1", "-s", "96"], capture_output=True).stdout.decode("utf-8").strip()

# Replace the line with "password_secret = " with the new password, keeping the existing content on the line
pw_parts = conf_lines[pw_index].split('=')
pw_parts[1] = f'{pw_parts[1].strip()} {new_password}\n'
conf_lines[pw_index] = '='.join(pw_parts)

# Open the file in write mode and overwrite it with the modified lines
with open('/etc/graylog/server/server.conf', 'w') as conf_file:
    conf_file.writelines(conf_lines)
print(new_password + ' is the hash associated with the password_secret variable in your server.conf file.\n')

# This is the section where we will ask the user for a password via an input statement
# Then use that string to generate a shasum 256 from the string
# and write it back to the server.conf file.

# Open the file in read mode
with open('/etc/graylog/server/server.conf', 'r') as hash_conf_file:
 hash_conf_lines = hash_conf_file.readlines()
    
# Find the line with "password_secret =" and store its index
hash_index = -1
for p, line in enumerate(hash_conf_lines):
  if line.startswith('root_password_sha2 ='):
    hash_index = p
    break  
print(p)

password_shasum = input("Please create a password to use with your Graylog account: ")
password_bytes = password_shasum.encode()

# Generate the SHA-256 hash
hash_object = hashlib.sha256()
hash_object.update(password_bytes)
password_hash = hash_object.hexdigest()

# Replace the line with "root_password_sha2 =" with the new password, keeping the existing content on the line
hash_parts = hash_conf_lines[hash_index].split('=')
hash_parts[1] = f'{hash_parts[1].strip()} {password_hash}\n'
hash_conf_lines[hash_index] = '='.join(hash_parts)

# Open the file in write mode and overwrite it with the modified lines
with open('/etc/graylog/server/server.conf', 'w') as hash_conf_file:
    hash_conf_file.writelines(hash_conf_lines)

#print the has for root_password_sha2
print(password_hash + ' is the hash associated with the root_password_sha2 variable in your server.conf file.\n')

# Reload the daemon and enable the Graylog Enterprise service
subprocess.run(["sudo", "systemctl", "daemon-reload"])
subprocess.run(["sudo", "systemctl", "enable", "graylog-server.service"])

# Start the Graylog Enterprise service
subprocess.run(["sudo", "systemctl", "start", "graylog-server.service"])

# Check the status of Graylog
subprocess.run(["sudo", "systemctl", "status", "graylog-server.service"])

# List all active services and grep for Graylog
#subprocess.run(["sudo", "systemctl", "--type=service", "--state=active", "|", "grep", "graylog"])

print('Graylog is up and running, navigate to ' + graylog_bind_address + "to log into your gralog server.\n')

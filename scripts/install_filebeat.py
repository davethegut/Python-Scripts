# Import the required modules
import subprocess
import os

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

#Check if filebeat is already installed

if os.path.exists("/etc/filebeat"):
    print("Filebeat is already installed.")
else:
    subprocess.run(["wget", "https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.8.1-amd64.deb"])
    subprocess.run(["dpkg", "-i", "filebeat-7.8.1-amd64.deb"])

# Start and enable filebeat service
subprocess.run(["systemctl", "start", "filebeat"])
subprocess.run(["systemctl", "enable", "filebeat"])
subprocess.run(["systemctl", "status", "filebeat.service"])
print("Filebeat has been installed and started successfully.")
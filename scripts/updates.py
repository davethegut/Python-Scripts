import subprocess
import os

def check_updates():
  # Get the list of available updates
  updates = subprocess.check_output(["apt", "list", "--upgradable"])

  # Print the list of available updates
  print(updates)

check_updates()

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

# update/upgrade the system
os.system("sudo apt update && apt upgrade")

print("update was a success")

import os
# Importing Fernet recipe to use for encryption
from cryptography.fernet import Fernet

# here we will be looking for some files
files = []

#for loop to create look for the files,
# 1st if statement used to skip over our script; 
# we also added an or logical operator so that we don't encrypt our key
# 2nd if statement used to only put files into our list, which are the files we want to encrypt
for file in os.listdir():
    if file == "fake.malware.py" or file == "secretkey.key" or file == "fake_decrypt.py":
        continue
#Here we will add the variable file to our "files" list above by appending
    if os.path.isfile(file):
        files.append(file)


print (files)

# here we are opening the secret_key as key and defining a new variable "secret_key"
with open("secretkey.key", "rb") as key:
    secret_key = key.read()

# This for loop will check every file in the variable files 
# Then we are opening the files in read binary with our function "thefile" 
# Then we are using the variable "contents" to be equal to thefile.read
# Then we are opening the files and decrypting them with fernet and our secret_key variable above
# And then lastly we are writing the decrypted contents back to the file 
for file in files:
    with open(file, "rb") as thefile:
        contents = thefile.read()
    contents_decrypted = Fernet(secret_key).decrypt(contents)
    with open(file, "wb") as thefile:
        thefile.write(contents_decrypted)
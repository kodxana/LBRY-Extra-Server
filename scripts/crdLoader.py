#!/usr/bin/env python

import platform
import os
import requests
import shutil
import zipfile
import stat

userOS = platform.system()

# Finding simple user OS information and default installation directories
if userOS == "Linux":
    home = os.path.expanduser("~")
    installPathCrd = home + "/.lbrycrd"
    installPathCrdBinary = home + "/.lbrycrd"
    slash = "/"
    binary_suffix = ""
elif userOS == "Windows":
    home = os.path.expanduser("~")
    installPathCrd = home + "\\AppData\\Roaming\\lbrycrd"
    installPathCrdBinary = home + "\\AppData\\Roaming\\lbrycrd"
    slash = "\\"
    binary_suffix = ".exe"


# Detecting installation at directed directory
def detect_crd():
    if not os.path.isdir(installPathCrd):
        return False
    if not os.path.isfile(installPathCrdBinary + slash + "lbrycrdd" + binary_suffix):
        return False
    return True


# Downloads and unzips lbrycrdd binary to installation folder
def fetch_crd_binary():
    response = requests.get('https://api.github.com/repos/lbryio/lbrycrd/releases/latest')
    info = response.json()
    assets = info['assets']
    matched = "No"
    for asset in assets:
        if userOS.lower() in asset['name']:
            download_link = asset['browser_download_url']
            local_filename = download_link.split('/')[-1]
            matched = "Yes"
    if matched != "Yes":
        print("Error: Could not match release binary with your OS. Manuel installation needed.")
        return
    if not os.path.isfile(local_filename):
        with requests.get(download_link, stream=True) as r:
            with open(local_filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
    with zipfile.ZipFile(local_filename, 'r') as zipped:
        zipped.extractall(installPathCrdBinary)
    print("The lbrycrdd binary has been installed.\n")


# Writes basic config file for lbrycrd inside it's installation directory
def build_config(password='lbry'):
    with open(installPathCrd + slash + "lbrycrd.conf", "w") as c:
        c.write("rpcuser=lbry")
        c.write("\nrpcpassword=" + str(password))
        if userOS is not "Windows":
            c.write("\ndaemon=1")
        c.write("\nserver=1")
        c.write("\ntxindex=1")


def start():
    print("Detecting installation...\n")
    if not detect_crd():
        print("The lbrycrdd binary not detected. Fetching.\n")
        fetch_crd_binary()
    if not detect_crd():
        print("Could not find lbrycrdd. Exiting.")
        return
    print("Found lbrycrdd at: "+installPathCrdBinary+"\n")
    user_password = input("Please enter password you want to use for LBRYcrd: ")
    build_config(user_password)
    cmd = installPathCrdBinary + slash + "lbrycrdd" + binary_suffix
    os.chmod(cmd, stat.S_IEXEC)
    output = os.popen(cmd).read()
    print(output)


start()

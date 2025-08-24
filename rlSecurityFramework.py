## Test specific Port ----

# import scapy.all as scapy
from scapy.all import IP, ICMP, sr1

# Send a SYN packet to port 80 on a remote host ------
# Build a simple ICMP packet
packet = IP(dst="8.8.8.8")/ICMP()
reply = sr1(packet, timeout=2)

if reply:
    print("Received reply:", reply.summary())
else:
    print("No response received.")

# -----

from cryptography.fernet import Fernet

# Generate a key and create a cipher suite
key = Fernet.generate_key()
cipher_suite = Fernet(key)
print("Encryption Key:", key.decode())

# Encrypt and decrypt a message
message = "Secure Message".encode()
encrypted_message = cipher_suite.encrypt(message)
print("Encrypted:", encrypted_message)

decrypted_message = cipher_suite.decrypt(encrypted_message)
print("Decrypted:", decrypted_message.decode())

# ------
import requests

# Send a GET request to a web server
response = requests.get('https://www.google.com')

# Check the response status code
if response.status_code == 200:
    print('Request successful')
else:
    print('Request failed')

# Print the response headers and content
print('Headers:', response.headers)
print('Content:', response.text)

# -------
import paramiko

hostname = 'example.com'
username = 'user'
password = 'password'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, username=username, password=password)

stdin, stdout, stderr = client.exec_command("echo 'Hello, Cybersecurity!'")
print(stdout.read().decode())

for line in stdout:
    print(line.strip())

client.close()

# -------
import nmap

nm = nmap.PortScanner()

# scan a target host for open ports
nm.scan('localhost', arguments='-p 22,80,443')

# print the state of the ports
for host in nm.all_hosts():
    print('Host : %s (%s)' % (host, nm[host].hostname()))
    print('State : %s' % nm[host].state())
    for proto in nm[host].all_protocols():
        print('Protocol : %s' % proto)
        ports = nm[host][proto].keys()
        for port in ports:
            print('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))

# ------- Using socket for Port Scanner ---
import socket

def scan_ports(target, start_port, end_port):
    print(f"Scanning {target} from port {start_port} to {end_port}")
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # Short timeout for responsiveness
        result = sock.connect_ex((target, port))
        if result == 0:
            print(f"Port {port}: Open")
        sock.close()

# Example usage: Scan localhost for ports 20 to 25
scan_ports("127.0.0.1", 20, 25)

# ------ Using socket for Encrypted Communication --
import socket

def scan_ports(target, start_port, end_port):
    print(f"Scanning {target} from port {start_port} to {end_port}")
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # Short timeout for responsiveness
        result = sock.connect_ex((target, port))
        if result == 0:
            print(f"Port {port}: Open")
        sock.close()

# Example usage: Scan localhost for ports 20 to 25
scan_ports("127.0.0.1", 20, 25)

# ---- automate reconnaissance, vulnerability scanning and exploit testing ---
# - Intrusion Detection Systems (IDS)
# - Malware Analysis and Forensics
# - Automated Vulnerability Scanning
# - Machine Learning in Cybersecurity
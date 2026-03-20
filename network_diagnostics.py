# Network Diagnostics Tool

import socket
import subprocess
import platform

# Function to check internet connection
def check_internet_connection():
    try:
        # Try to connect to a public DNS server
        socket.create_connection(('8.8.8.8', 53))
        return True
    except OSError:
        return False

# Function to get the local machine's IP address
def get_local_ip_address():
    hostname = socket.gethostname()  
    local_ip = socket.gethostbyname(hostname)  
    return local_ip

# Function to perform a ping test
def ping_test(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '4', host]  
    return subprocess.call(command) == 0

# Main function
def main():
    internet_status = check_internet_connection()
    if internet_status:
        print("Internet is connected.")
    else:
        print("Internet is not connected.")

    local_ip = get_local_ip_address()
    print(f"Local IP Address: {local_ip}")

    # Example ping test
    ping_host = 'google.com'
    if ping_test(ping_host):
        print(f"Successfully pinged {ping_host}")
    else:
        print(f"Failed to ping {ping_host}")

if __name__ == '__main__':
    main()
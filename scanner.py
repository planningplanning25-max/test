import subprocess
import socket
import netifaces
import threading
import platform
import re
from concurrent.futures import ThreadPoolExecutor

def get_local_network():
    try:
        gateways = netifaces.gateways()
        default_gateway = gateways.get('default')
        if not default_gateway or netifaces.AF_INET not in default_gateway:
            return None

        interface = default_gateway[netifaces.AF_INET][1]
        iface_details = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if not iface_details:
            return None

        ip = iface_details[0]['addr']
        netmask = iface_details[0]['netmask']

        # Determine base IP for /24 network
        base_ip = ".".join(ip.split('.')[:-1])
        return base_ip
    except Exception:
        return None

def get_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except socket.herror:
        return "Unknown"

def ping_ip(ip):
    """
    Returns (ip, status)
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', '500', ip]
    try:
        output = subprocess.run(command, capture_output=True, text=True, timeout=1)
        if output.returncode == 0:
            return ip, True
    except:
        pass
    return ip, False

def get_mac_from_arp(target_ip):
    """
    Tries to find MAC address from the system ARP cache
    """
    try:
        output = subprocess.check_output(['arp', '-a', target_ip], text=True, stderr=subprocess.STDOUT)
        # Search for MAC address pattern
        mac_pattern = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"
        match = re.search(mac_pattern, output)
        if match:
            return match.group(0)
    except:
        pass
    return "Unknown"

def scan(base_ip):
    """
    Scans the /24 network using Ping and ARP cache
    """
    if not base_ip:
        return []

    devices_list = []
    ips_to_scan = [f"{base_ip}.{i}" for i in range(1, 255)]

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(ping_ip, ips_to_scan))

    for ip, active in results:
        if active:
            hostname = get_hostname(ip)
            mac = get_mac_from_arp(ip)
            devices_list.append({
                "ip": ip,
                "mac": mac,
                "hostname": hostname
            })

    return devices_list

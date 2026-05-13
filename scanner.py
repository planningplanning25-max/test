import scapy.all as scapy
import socket
import netifaces
import threading

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

        # Calculate CIDR
        cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))
        network = ".".join(ip.split('.')[:-1]) + ".0/" + str(cidr)
        return network
    except Exception:
        return None

def get_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except socket.herror:
        return "Unknown"

def scan(network):
    arp_request = scapy.ARP(pdst=network)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    devices_list = []
    for element in answered_list:
        ip = element[1].psrc
        device_info = {"ip": ip, "mac": element[1].hwsrc, "hostname": get_hostname(ip)}
        devices_list.append(device_info)
    return devices_list

import socket
import netifaces

def get_ip():
    try:
        addrs = netifaces.ifaddresses('wlan0')
        ip = addrs[netifaces.AF_INET][0]['addr']
        return ip
    except ValueError:
        addrs = netifaces.ifaddresses('ra0')
        ip = addrs[netifaces.AF_INET][0]['addr']
        return ip


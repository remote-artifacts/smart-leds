import network

def config_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='Sensor')
    ap.config(authmode=3, password='123456789')


def connect(bssid, password, ip='192.168.1.250', mask='255.255.255.0', gateway='192.168.1.1'):
    station = network.WLAN(network.STA_IF)
    if not station.active():
        station.active(True)
    station.ifconfig((ip, mask, gateway, gateway))
    station.connect(bssid, password)
    return station


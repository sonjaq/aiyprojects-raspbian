import sys, socket, select, time

def wake(ip_address="192.168.164", live_id="avleaf@live.com"):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(0)
    s.bind(("", 0))
    s.connect((ip_address, 5050))
    
    encoded_live_id = live_id.encode() 
    
    power_payload = b'\x00' + chr(len(encoded_live_id)).encode() + encoded_live_id + b'\x00'
    power_header = b'\xdd\x02\x00' + chr(len(power_payload)).encode() + b'\x00\x00'
    power_packet = power_header + power_payload
    for i in range(0,5):
        s.send(power_packet)
        time.sleep(1)


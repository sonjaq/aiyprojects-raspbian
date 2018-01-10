import socket
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

"""
Borrowed, modified from https://github.com/Schamper/xbox-remote-power
"""
def wake(ip_address, live_device_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(0)
    s.bind(("", 0))
    s.connect((ip_address, 5050))

    encoded_live_device_id = live_device_id.encode()

    power_payload = b'\x00' + chr(len(encoded_live_device_id)).encode() + encoded_live_device_id + b'\x00'
    power_header = b'\xdd\x02\x00' + chr(len(power_payload)).encode() + b'\x00\x00'
    power_packet = power_header + power_payload
    for i in range(0,5):
        logging.info("PINGING XBOX")
        s.send(power_packet)
        time.sleep(1)


# osi_model/physical.py
import socket

class PhysicalLayer:
    def send(self, data):
        print("[Physical Layer] Sending bits over the network...")
        return data.encode('utf-8')
    
    def receive(self, data):
        print("[Physical Layer] Receiving bits from the network...")
        return data.decode('utf-8')

# osi_model/data_link.py
class DataLinkLayer:
    def __init__(self):
        self.mac_address = "AA:BB:CC:DD:EE:FF"
    
    def send(self, data):
        print("[Data Link Layer] Adding MAC address and framing...")
        frame = f"{self.mac_address}:{data}"
        return frame
    
    def receive(self, data):
        print("[Data Link Layer] Removing MAC address and verifying frame...")
        _, payload = data.split(':', 1)
        return payload

# osi_model/network.py
class NetworkLayer:
    def __init__(self):
        self.ip_address = "192.168.1.1"
    
    def send(self, data):
        print("[Network Layer] Adding IP address and routing...")
        packet = f"{self.ip_address}:{data}"
        return packet
    
    def receive(self, data):
        print("[Network Layer] Removing IP address and processing packet...")
        _, payload = data.split(':', 1)
        return payload

# osi_model/transport.py
class TransportLayer:
    def send(self, data):
        print("[Transport Layer] Adding sequencing and error handling...")
        segment = f"SEQ1:{data}"
        return segment
    
    def receive(self, data):
        print("[Transport Layer] Verifying sequence and handling errors...")
        _, payload = data.split(':', 1)
        return payload

# osi_model/session.py
class SessionLayer:
    def send(self, data):
        print("[Session Layer] Managing session state...")
        session_data = f"SESSION:{data}"
        return session_data
    
    def receive(self, data):
        print("[Session Layer] Handling session management...")
        _, payload = data.split(':', 1)
        return payload

# osi_model/presentation.py
class PresentationLayer:
    def send(self, data):
        print("[Presentation Layer] Encoding and compressing data...")
        encoded_data = data[::-1]  # Simple reversible transformation (reversal as encoding)
        return encoded_data
    
    def receive(self, data):
        print("[Presentation Layer] Decoding and decompressing data...")
        decoded_data = data[::-1]
        return decoded_data

# osi_model/application.py
class ApplicationLayer:
    def send(self, message):
        print("[Application Layer] Preparing application data...")
        return f"HTTP_REQUEST:{message}"
    
    def receive(self, data):
        print("[Application Layer] Processing application data...")
        _, payload = data.split(':', 1)
        return payload

# osi_model/main.py
'''from physical import PhysicalLayer
from data_link import DataLinkLayer
from network import NetworkLayer
from transport import TransportLayer
from session import SessionLayer
from presentation import PresentationLayer
from application import ApplicationLayer'''

def main():
    app_layer = ApplicationLayer()
    pres_layer = PresentationLayer()
    sess_layer = SessionLayer()
    trans_layer = TransportLayer()
    net_layer = NetworkLayer()
    data_link_layer = DataLinkLayer()
    phys_layer = PhysicalLayer()

    # Simulating data transmission
    message = "Hello, OSI Model!"
    print("\n--- Sending Data ---\n")
    data = app_layer.send(message)
    data = pres_layer.send(data)
    data = sess_layer.send(data)
    data = trans_layer.send(data)
    data = net_layer.send(data)
    data = data_link_layer.send(data)
    data = phys_layer.send(data)

    # Simulating data reception
    print("\n--- Receiving Data ---\n")
    data = phys_layer.receive(data)
    data = data_link_layer.receive(data)
    data = net_layer.receive(data)
    data = trans_layer.receive(data)
    data = sess_layer.receive(data)
    data = pres_layer.receive(data)
    data = app_layer.receive(data)

    print("\nFinal message received:", data)

if __name__ == "__main__":
    main()

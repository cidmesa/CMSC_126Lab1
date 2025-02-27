# data_link_layer.py
import json
import hashlib

class DataLinkLayer:
    def __init__(self, mac_address):
        self.mac_address = mac_address
        self.physical_layer = None
        self.network_layer = None
        # Simple MAC table (destination MAC -> is_local)
        self.mac_table = {}
    
    def connect_to_physical_layer(self, physical_layer):
        self.physical_layer = physical_layer
        physical_layer.connect_to_data_link_layer(self)
    
    def connect_to_network_layer(self, network_layer):
        self.network_layer = network_layer
    
    def add_mac_entry(self, mac_address, is_local=False):
        self.mac_table[mac_address] = is_local
    
    def create_frame(self, data, destination_mac):
        # Frame format:
        # {
        #   'source_mac': <sender MAC>,
        #   'destination_mac': <destination MAC>,
        #   'data': <payload>,
        #   'checksum': <checksum>
        # }
        frame = {
            'source_mac': self.mac_address,
            'destination_mac': destination_mac,
            'data': data,
            'checksum': self._calculate_checksum(data)
        }
        return json.dumps(frame).encode()
    
    def _calculate_checksum(self, data):
        # Calculate a simple checksum for data integrity
        if isinstance(data, bytes):
            return hashlib.md5(data).hexdigest()
        else:
            return hashlib.md5(str(data).encode()).hexdigest()
    
    def send_to_physical(self, data, destination_mac):
        frame = self.create_frame(data, destination_mac)
        if self.physical_layer:
            self.physical_layer.send_data(frame)
            print(f"Frame sent to {destination_mac}")
    
    def receive_from_physical(self, frame_data):
        try:
            # Parse the frame
            frame = json.loads(frame_data.decode())
            
            # Verify it's for us or broadcast
            if frame['destination_mac'] != self.mac_address and frame['destination_mac'] != 'FF:FF:FF:FF:FF:FF':
                print(f"Frame not for us (for {frame['destination_mac']}), dropping")
                return
            
            # Verify checksum
            calculated_checksum = self._calculate_checksum(frame['data'])
            if calculated_checksum != frame['checksum']:
                print("Checksum mismatch, dropping frame")
                return
            
            print(f"Frame received from {frame['source_mac']}")
            
            # Forward data to the network layer
            if self.network_layer:
                self.network_layer.receive_from_data_link(frame['data'])
                
        except Exception as e:
            print(f"Data link layer error: {e}")

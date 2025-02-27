# network_layer.py
import json

class NetworkLayer:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.routing_table = {}  # Maps IP to next hop
        self.data_link_layer = None
        self.transport_layer = None
    
    def connect_to_data_link_layer(self, data_link_layer):
        self.data_link_layer = data_link_layer
        data_link_layer.connect_to_network_layer(self)
    
    def connect_to_transport_layer(self, transport_layer):
        self.transport_layer = transport_layer
    
    def add_route(self, destination_ip, next_hop_mac):
        """Add a routing rule: packets to destination_ip go to next_hop_mac"""
        self.routing_table[destination_ip] = next_hop_mac
    
    def create_packet(self, data, destination_ip):
        # IP Packet format:
        # {
        #   'source_ip': <sender IP>,
        #   'destination_ip': <destination IP>,
        #   'ttl': <time to live>,
        #   'data': <payload>
        # }
        packet = {
            'source_ip': self.ip_address,
            'destination_ip': destination_ip,
            'ttl': 64,  # Default TTL
            'data': data
        }
        return packet
    
    def send_to_data_link(self, packet, destination_ip):
        # Find the next hop MAC from routing table
        if destination_ip in self.routing_table:
            next_hop_mac = self.routing_table[destination_ip]
        else:
            # Default gateway or broadcast if no route found
            next_hop_mac = 'FF:FF:FF:FF:FF:FF'
        
        # Serialize and send the packet
        serialized_packet = json.dumps(packet)
        if self.data_link_layer:
            self.data_link_layer.send_to_physical(serialized_packet, next_hop_mac)
            print(f"Packet sent to {destination_ip} via {next_hop_mac}")
    
    def receive_from_data_link(self, data):
        try:
            # Parse the packet
            packet = json.loads(data)
            
            # Check if the packet is for us
            if packet['destination_ip'] != self.ip_address:
                print(f"Packet not for us (for {packet['destination_ip']}), dropping")
                return
            
            # Decrement TTL
            packet['ttl'] -= 1
            if packet['ttl'] <= 0:
                print("TTL expired, dropping packet")
                return
            
            print(f"Packet received from {packet['source_ip']}")
            
            # Forward data to the transport layer
            if self.transport_layer:
                self.transport_layer.receive_from_network(packet['data'])
                
        except Exception as e:
            print(f"Network layer error: {e}")
    
    def send_to_transport(self, data, destination_ip):
        packet = self.create_packet(data, destination_ip)
        self.send_to_data_link(packet, destination_ip)

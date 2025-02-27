# osi_stack.py
from physical_layer import PhysicalLayer
from data_link_layer import DataLinkLayer
from network_layer import NetworkLayer
from transport_layer import TransportLayer
from session_layer import SessionLayer
from presentation_layer import PresentationLayer
from application_layer import ApplicationLayer

class OSIStack:
    def __init__(self, is_server=False, host='127.0.0.1', port=12345, mac_address='00:00:00:00:00:01', ip_address='192.168.1.1'):
        # Create all layers
        self.physical = PhysicalLayer(is_server, host, port)
        self.data_link = DataLinkLayer(mac_address)
        self.network = NetworkLayer(ip_address)
        self.transport = TransportLayer()
        self.session = SessionLayer()
        self.presentation = PresentationLayer()
        self.application = ApplicationLayer()
        
        # Connect layers
        self.data_link.connect_to_physical_layer(self.physical)
        self.network.connect_to_data_link_layer(self.data_link)
        self.transport.connect_to_network_layer(self.network)
        self.session.connect_to_transport_layer(self.transport)
        self.presentation.connect_to_session_layer(self.session)
        self.application.connect_to_presentation_layer(self.presentation)
        
        # Initialize routing
        self.data_link.add_mac_entry(mac_address, True)  # Local MAC
    
    def initialize(self):
        """Initialize the stack (start the physical layer)"""
        self.physical.initialize()
    
    def add_route(self, destination_ip, next_hop_mac):
        """Add a route to the network layer"""
        self.network.add_route(destination_ip, next_hop_mac)
    
    def register_application_handler(self, method, handler):
        """Register an application handler"""
        self.application.register_handler(method, handler)
    
    def send_request(self, method, path, peer_ip, headers=None, body=None):
        """Send an HTTP-like request"""
        return self.application.send_request(method, path, peer_ip, headers, body)
    
    def close(self):
        """Shut down the stack"""
        self.physical.close()

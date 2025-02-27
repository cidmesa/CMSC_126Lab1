# physical_layer.py
import socket
import struct
from threading import Thread

class PhysicalLayer:
    def __init__(self, is_server=False, host='127.0.0.1', port=12345):
        self.is_server = is_server
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.data_link_layer = None
        self.server_socket = None  # For storing the server listening socket
    
    def connect_to_data_link_layer(self, data_link_layer):
        self.data_link_layer = data_link_layer
    
    def initialize(self):
        if self.is_server:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            print(f"Server listening on {self.host}:{self.port}")
            
            # Start a thread to accept connections instead of blocking
            Thread(target=self._accept_connections).start()
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            self.connected = True
            
            # Start receiving thread
            Thread(target=self.receive_data).start()
    
    def _accept_connections(self):
        """Accept client connections in a separate thread"""
        client_socket, addr = self.server_socket.accept()
        self.socket = client_socket
        print(f"Connection from {addr}")
        self.connected = True
        
        # Start receiving thread
        Thread(target=self.receive_data).start()
    
    def send_data(self, data):
        # Convert data to bitstream (bytes)
        if isinstance(data, str):
            bit_data = data.encode()
        else:
            bit_data = data
            
        # Only send if we're connected
        if self.connected and self.socket:
            # Send data length first, then data
            data_len = len(bit_data)
            self.socket.sendall(struct.pack('!I', data_len))
            self.socket.sendall(bit_data)
        else:
            print("Cannot send data: not connected")
        
    def receive_data(self):
        while self.connected:
            try:
                # First receive the length of incoming data
                length_bytes = self.socket.recv(4)
                if not length_bytes:
                    break
                
                data_length = struct.unpack('!I', length_bytes)[0]
                
                # Receive the actual data
                received_data = b''
                while len(received_data) < data_length:
                    packet = self.socket.recv(data_length - len(received_data))
                    if not packet:
                        break
                    received_data += packet
                
                if self.data_link_layer:
                    self.data_link_layer.receive_from_physical(received_data)
            
            except Exception as e:
                print(f"Physical layer receive error: {e}")
                self.connected = False
                break
    
    def close(self):
        self.connected = False
        if self.socket:
            self.socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("Physical connection closed")
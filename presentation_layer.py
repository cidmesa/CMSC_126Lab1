# presentation_layer.py
import json
import base64

class PresentationLayer:
    def __init__(self):
        self.session_layer = None
        self.application_layer = None
        self.encoding = 'utf-8'
        self.compression_enabled = False
    
    def connect_to_session_layer(self, session_layer):
        self.session_layer = session_layer
        session_layer.connect_to_presentation_layer(self)
    
    def connect_to_application_layer(self, application_layer):
        self.application_layer = application_layer
    
    def encrypt(self, data):
        """Simple XOR 'encryption' - not secure but demonstrates the concept"""
        key = b'SECRET'
        if isinstance(data, str):
            data = data.encode(self.encoding)
            
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        
        # Base64 encode to make it transportable
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, data):
        """Decrypt data that was encrypted with the encrypt method"""
        key = b'SECRET'
        # Base64 decode
        try:
            data = base64.b64decode(data)
            
            decrypted = bytearray()
            for i, byte in enumerate(data):
                decrypted.append(byte ^ key[i % len(key)])
            
            return decrypted.decode(self.encoding)
        except:
            # If it's not properly encrypted/encoded, return as is
            return data
    
    def compress(self, data):
        """Simple compression placeholder - in a real implementation you would use zlib or similar"""
        if self.compression_enabled:
            # This is a simplified placeholder
            return f"COMPRESSED:{data}"
        return data
    
    def decompress(self, data):
        """Decompress data that was compressed with the compress method"""
        if self.compression_enabled and isinstance(data, str) and data.startswith("COMPRESSED:"):
            return data[11:]  # Remove the "COMPRESSED:" prefix
        return data
    
    def encode(self, data):
        """Encode data for transmission"""
        # Wrap in a presentation layer envelope
        envelope = {
            'encoding': self.encoding,
            'compressed': self.compression_enabled,
            'encrypted': True,
            'data': self.encrypt(self.compress(data))
        }
        
        return json.dumps(envelope)
    
    def decode(self, data):
        """Decode received data"""
        try:
            envelope = json.loads(data)
            
            # Extract the metadata
            encoding = envelope.get('encoding', self.encoding)
            compressed = envelope.get('compressed', False)
            encrypted = envelope.get('encrypted', False)
            
            # Process the data according to the metadata
            result = envelope['data']
            
            if encrypted:
                result = self.decrypt(result)
            
            if compressed:
                result = self.decompress(result)
            
            return result
        
        except Exception as e:
            print(f"Presentation layer decode error: {e}")
            # If decoding fails, return the raw data
            return data
    
    def send_to_session(self, data, peer_ip):
        """Encode and send data through the session layer"""
        encoded_data = self.encode(data)
        
        if self.session_layer:
            return self.session_layer.send_to_presentation(encoded_data, peer_ip)
        
        return False
    
    def receive_from_session(self, data, session_id):
        """Receive and decode data from the session layer"""
        decoded_data = self.decode(data)
        
        print(f"Data received and decoded in presentation layer")
        
        # Forward to the application layer
        if self.application_layer:
            self.application_layer.receive_from_presentation(decoded_data, session_id)
    
    def send_to_application(self, data, peer_ip):
        """Send data to the application layer after appropriate processing"""
        if self.session_layer:
            return self.send_to_session(data, peer_ip)
        return False

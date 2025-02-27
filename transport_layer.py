# transport_layer.py
import json

class TransportLayer:
    def __init__(self):
        self.network_layer = None
        self.session_layer = None
        self.sequence_number = 0
        self.expected_sequence = 0
        self.buffer = {}
        self.max_retries = 3
    
    def connect_to_network_layer(self, network_layer):
        self.network_layer = network_layer
        network_layer.connect_to_transport_layer(self)
    
    def connect_to_session_layer(self, session_layer):
        self.session_layer = session_layer
    
    def create_segment(self, data):
        # TCP-like segment format:
        # {
        #   'sequence': <sequence number>,
        #   'ack': <acknowledgment number>,
        #   'flags': <control flags>,
        #   'window': <window size>,
        #   'data': <payload>
        # }
        segment = {
            'sequence': self.sequence_number,
            'ack': 0,
            'flags': {'SYN': False, 'ACK': False, 'FIN': False},
            'window': 64,  # Default window size
            'data': data
        }
        
        # Increment sequence number for next segment
        self.sequence_number += 1
        
        return segment
    
    def send_to_network(self, segment, destination_ip):
        # Serialize and send the segment
        serialized_segment = json.dumps(segment)
        if self.network_layer:
            self.network_layer.send_to_transport(serialized_segment, destination_ip)
            print(f"Segment {segment['sequence']} sent")
    
    def receive_from_network(self, data):
        try:
            # Parse the segment
            segment = json.loads(data)
            
            # Check for ACK flag
            if segment['flags']['ACK']:
                print(f"ACK received for segment {segment['ack']}")
                # Remove from retransmission buffer if needed
                if segment['ack'] in self.buffer:
                    del self.buffer[segment['ack']]
                return
            
            # Process regular data segment
            print(f"Segment {segment['sequence']} received")
            
            # Send ACK
            ack_segment = {
                'sequence': self.sequence_number,
                'ack': segment['sequence'],
                'flags': {'SYN': False, 'ACK': True, 'FIN': False},
                'window': 64,
                'data': ''
            }
            
            # Increment sequence number for next segment
            self.sequence_number += 1
            
            # Send acknowledgment
            if self.network_layer:
                self.network_layer.send_to_transport(json.dumps(ack_segment), segment['source_ip'] if 'source_ip' in segment else "unknown")
            
            # Check if this is the segment we're expecting
            if segment['sequence'] == self.expected_sequence:
                self.expected_sequence += 1
                
                # Forward data to the session layer
                if self.session_layer and 'data' in segment:
                    self.session_layer.receive_from_transport(segment['data'])
                
                # Check if we have buffered segments that can now be processed
                while self.expected_sequence in self.buffer:
                    buffered_segment = self.buffer[self.expected_sequence]
                    del self.buffer[self.expected_sequence]
                    self.expected_sequence += 1
                    
                    # Forward data from buffered segment
                    if self.session_layer and 'data' in buffered_segment:
                        self.session_layer.receive_from_transport(buffered_segment['data'])
            
            # If not the expected sequence, buffer it
            elif segment['sequence'] > self.expected_sequence:
                self.buffer[segment['sequence']] = segment
                print(f"Segment {segment['sequence']} buffered (expecting {self.expected_sequence})")
            
            # Else it's a duplicate or old segment, just acknowledge it
                
        except Exception as e:
            print(f"Transport layer error: {e}")
    
    def send_to_session(self, data, destination_ip):
        # Create segment
        segment = self.create_segment(data)
        
        # Add to retransmission buffer
        self.buffer[segment['sequence']] = segment
        
        # Send segment
        self.send_to_network(segment, destination_ip)

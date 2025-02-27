# session_layer.py
import json
import time
import random

class SessionLayer:
    def __init__(self):
        self.transport_layer = None
        self.presentation_layer = None
        self.sessions = {}  # Maps session_id to session state
        self.current_session_id = None
    
    def connect_to_transport_layer(self, transport_layer):
        self.transport_layer = transport_layer
        transport_layer.connect_to_session_layer(self)
    
    def connect_to_presentation_layer(self, presentation_layer):
        self.presentation_layer = presentation_layer
    
    def create_session(self, peer_ip):
        """Initialize a new session with a peer"""
        session_id = f"{random.randint(1000, 9999)}"
        
        self.sessions[session_id] = {
            'peer_ip': peer_ip,
            'state': 'ESTABLISHED',
            'last_activity': time.time()
        }
        
        self.current_session_id = session_id
        return session_id
    
    def close_session(self, session_id):
        """Close an existing session"""
        if session_id in self.sessions:
            self.sessions[session_id]['state'] = 'CLOSED'
            print(f"Session {session_id} closed")
            
            if self.current_session_id == session_id:
                self.current_session_id = None
    
    def send_to_transport(self, data, session_id=None):
        """Send data through the session"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id or session_id not in self.sessions:
            print("No active session")
            return False
        
        if self.sessions[session_id]['state'] != 'ESTABLISHED':
            print(f"Session {session_id} not in ESTABLISHED state")
            return False
        
        # Update session activity time
        self.sessions[session_id]['state'] = 'ESTABLISHED'
        self.sessions[session_id]['last_activity'] = time.time()
        
        # Package data with session information
        session_data = {
            'session_id': session_id,
            'data': data
        }
        
        # Send through transport layer
        if self.transport_layer:
            peer_ip = self.sessions[session_id]['peer_ip']
            self.transport_layer.send_to_session(json.dumps(session_data), peer_ip)
            print(f"Data sent through session {session_id}")
            return True
        
        return False
    
    def receive_from_transport(self, data):
        try:
            # Parse session data
            session_data = json.loads(data)
            
            session_id = session_data.get('session_id')
            
            # Check if this is a known session
            if session_id not in self.sessions:
                # Create new session if it doesn't exist
                self.sessions[session_id] = {
                    'peer_ip': "unknown",  # We'll update this later
                    'state': 'ESTABLISHED',
                    'last_activity': time.time()
                }
                print(f"New session {session_id} created")
            
            # Update session state
            self.sessions[session_id]['last_activity'] = time.time()
            
            print(f"Data received through session {session_id}")
            
            # Forward data to the presentation layer
            if self.presentation_layer and 'data' in session_data:
                self.presentation_layer.receive_from_session(session_data['data'], session_id)
                
        except Exception as e:
            print(f"Session layer error: {e}")
    
    def send_to_presentation(self, data, peer_ip):
        """Create a session if needed and send data to the presentation layer"""
        if not self.current_session_id:
            session_id = self.create_session(peer_ip)
        else:
            session_id = self.current_session_id
        
        return self.send_to_transport(data, session_id)

# application_layer.py
import json

class ApplicationLayer:
    def __init__(self):
        self.presentation_layer = None
        self.handlers = {}  # Maps HTTP-like methods to handler functions
    
    def connect_to_presentation_layer(self, presentation_layer):
        self.presentation_layer = presentation_layer
        presentation_layer.connect_to_application_layer(self)
    
    def register_handler(self, method, handler):
        """Register a handler function for a specific HTTP-like method"""
        self.handlers[method] = handler
    
    def create_request(self, method, path, headers=None, body=None):
        """Create an HTTP-like request"""
        if headers is None:
            headers = {}
        
        request = {
            'type': 'request',
            'method': method,
            'path': path,
            'headers': headers,
            'body': body
        }
        
        return json.dumps(request)
    
    def create_response(self, status_code, status_message, headers=None, body=None):
        """Create an HTTP-like response"""
        if headers is None:
            headers = {}
        
        response = {
            'type': 'response',
            'status_code': status_code,
            'status_message': status_message,
            'headers': headers,
            'body': body
        }
        
        return json.dumps(response)
    
    def send_request(self, method, path, peer_ip, headers=None, body=None):
        """Send an HTTP-like request to a peer"""
        request = self.create_request(method, path, headers, body)
        
        if self.presentation_layer:
            return self.presentation_layer.send_to_application(request, peer_ip)
        
        return False
    
    def send_response(self, status_code, status_message, peer_ip, headers=None, body=None):
        """Send an HTTP-like response to a peer"""
        response = self.create_response(status_code, status_message, headers, body)
        
        if self.presentation_layer:
            return self.presentation_layer.send_to_application(response, peer_ip)
        
        return False
    
    def receive_from_presentation(self, data, session_id):
        """Process data received from the presentation layer"""
        try:
            message = json.loads(data)
            
            # Determine if this is a request or response
            if message.get('type') == 'request':
                self._handle_request(message, session_id)
            elif message.get('type') == 'response':
                self._handle_response(message, session_id)
            else:
                print("Unknown message type received")
                
        except Exception as e:
            print(f"Application layer error: {e}")
    
    def _handle_request(self, request, session_id):
        """Handle an incoming HTTP-like request"""
        method = request.get('method', '')
        path = request.get('path', '')
        
        print(f"Request received: {method} {path}")
        
        # Find a handler for this method
        if method in self.handlers:
            # Call the handler with the request
            response = self.handlers[method](request)
            
            # Get peer IP from the session
            peer_ip = "unknown"
            if self.presentation_layer and self.presentation_layer.session_layer:
                if session_id in self.presentation_layer.session_layer.sessions:
                    peer_ip = self.presentation_layer.session_layer.sessions[session_id]['peer_ip']
            
            # Send the response
            if isinstance(response, tuple) and len(response) >= 2:
                status_code, status_message = response[0], response[1]
                headers = response[2] if len(response) > 2 else None
                body = response[3] if len(response) > 3 else None
                
                self.send_response(status_code, status_message, peer_ip, headers, body)
            else:
                print("Invalid response format from handler")
        else:
            print(f"No handler for method: {method}")
    
    def _handle_response(self, response, session_id):
        """Handle an incoming HTTP-like response"""
        status_code = response.get('status_code', 0)
        status_message = response.get('status_message', '')
        body = response.get('body', '')
        
        print(f"Response received: {status_code} {status_message}")
        print(f"Body: {body}")
        
        # Additional response handling logic would go here

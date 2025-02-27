# examples.py
import time
from osi_stack import OSIStack

# Sample Server Implementation
def create_server():
    # Create server stack
    server = OSIStack(
        is_server=True,
        host='127.0.0.1',
        port=12345,
        mac_address='00:00:00:00:00:01',
        ip_address='192.168.1.1'
    )
    
    # Add route to client
    server.add_route('192.168.1.2', '00:00:00:00:00:02')
    
    # Define a GET handler
    def handle_get(request):
        path = request.get('path', '')
        
        if path == '/hello':
            return 200, 'OK', None, 'Hello, World!'
        elif path == '/time':
            return 200, 'OK', None, f"The time is {time.strftime('%H:%M:%S')}"
        else:
            return 404, 'Not Found', None, 'Resource not found'
    
    # Define a POST handler
    def handle_post(request):
        path = request.get('path', '')
        body = request.get('body', '')
        
        if path == '/echo':
            return 200, 'OK', None, f"You sent: {body}"
        else:
            return 404, 'Not Found', None, 'Resource not found'
    
    # Register handlers
    server.register_application_handler('GET', handle_get)
    server.register_application_handler('POST', handle_post)
    
    # Initialize the server
    server.initialize()
    
    print("Server initialized and ready")
    
    return server

# Sample Client Implementation
def create_client():
    # Create client stack
    client = OSIStack(
        is_server=False,
        host='127.0.0.1',
        port=12345,
        mac_address='00:00:00:00:00:02',
        ip_address='192.168.1.2'
    )
    
    # Add route to server
    client.add_route('192.168.1.1', '00:00:00:00:00:01')
    
    # Initialize the client
    client.initialize()
    
    print("Client initialized and ready")
    
    return client

# Example usage
if __name__ == "__main__":
    server = create_server()
    time.sleep(1)  # Give server time to start
    
    client = create_client()
    
    # Send requests from client to server
    response = client.send_request('GET', '/hello', '192.168.1.1')
    print("Response:", response)
    
    response = client.send_request('GET', '/time', '192.168.1.1')
    print("Response:", response)
    
    response = client.send_request('POST', '/echo', '192.168.1.1', body='Hello Server!')
    print("Response:", response)
    
    # Clean up
    client.close()
    server.close()

from flask import Flask, request, send_file, abort
import os
import socket
import threading
import ssl
from werkzeug.utils import secure_filename

app = Flask(__name__)
HOST = 'localhost'
PORT = 27015
BUFFER_SIZE = 8192
FILES_DIRECTORY = 'server_files'

# Configure Flask app
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1 MB
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']  # Example extensions

def receive_file(connection, filename):
    
    try:
        file_path = os.path.join(FILES_DIRECTORY, filename)
        
        # Receive file size from the server
        file_size = int(connection.recv(BUFFER_SIZE).decode())
        
        # Receive file content from the server and save it
        with open(file_path, 'wb') as file:
            received_size = 0
            while received_size < file_size:
                data = connection.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
                received_size += len(data)
        
        print(f"File '{filename}' downloaded successfully.")

        connection.sendall('Upload complete'.encode())
    except Exception as e:
        print(f"Error downloading file '{filename}': {e}")

def send_file(connection, filename):
    try:
        file_path = os.path.join(FILES_DIRECTORY, filename)
        print(f"Sending file: {file_path}")
        file_size = os.path.getsize(file_path)
        connection.sendall(str(file_size).encode())
        with open(file_path, 'rb') as file:
            connection.sendfile(file)
        print(f"File '{filename}' sent successfully.")
    except Exception as e:
        print(f"Error sending file '{filename}': {e}")

def handle_client(client_socket):
    try:
        while True:
            choice = client_socket.recv(BUFFER_SIZE).decode()
            if not choice:
                break
            if choice == 'upload':
                filename = client_socket.recv(BUFFER_SIZE).decode()
                receive_file(client_socket, filename)
            elif choice == 'download':
                filename = client_socket.recv(BUFFER_SIZE).decode()
                send_file(client_socket, filename)
            elif choice == 'quit':
                print("Client requested to quit. Closing connection.")
                client_socket.sendall(b'Quit successful. Closing connection.')
                break
            else:
                print("Invalid choice.")
    except ConnectionResetError:
        print("Client closed the connection unexpectedly.")
    except Exception as e:
        print(f"Error handling client request: {e}")
    finally:
        # Ensure the socket is closed properly
        try:
            client_socket.close()
        except Exception as e:
            print(f"Error closing client socket: {e}")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        abort(400, "No file part")
    file = request.files['file']
    if file.filename == '':
        abort(400, "No selected file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(FILES_DIRECTORY, filename))
        return 'File uploaded successfully.'
    else:
        abort(400, "File type not allowed")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_EXTENSIONS']

@app.route('/request/<filename>', methods=['GET'])
def request_file(filename):
    file_path = os.path.join(FILES_DIRECTORY, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, "File not found.")

@app.route('/')
def index():
    return "This is client-server file sharing system"

def start_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server is listening on {HOST}:{PORT}")
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection established with {client_address}")
                cert_path = os.path.join('certs', 'cert.pem')
                key_path = os.path.join('certs', 'key.pem')
                
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile=cert_path, keyfile=key_path)
                ssl_client_socket = context.wrap_socket(client_socket, server_side=True)
                client_handler = threading.Thread(target=handle_client, args=(ssl_client_socket,))
                client_handler.start()
        finally:
            server_socket.close()

if __name__ == "__main__":
    if not os.path.exists(FILES_DIRECTORY):
        os.makedirs(FILES_DIRECTORY)
    socket_server_thread = threading.Thread(target=start_socket_server)
    socket_server_thread.start()
    app.run()

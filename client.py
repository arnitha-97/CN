import socket
import ssl
import os
from art import logo

SERVER_HOST = 'localhost'
SERVER_PORT = 27015
BUFFER_SIZE = 8192

def upload_file(filename):
    try:
        # Use the certificate from the certs/ directory
        cert_path = os.path.join('certs', 'cert.pem')
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cert_path)
        with socket.create_connection((SERVER_HOST, SERVER_PORT)) as server_socket:
            with context.wrap_socket(server_socket, server_hostname=SERVER_HOST) as ssl_socket:
                # Send upload command to the server
                ssl_socket.sendall(b'upload')
                
                ssl_socket.sendall(os.path.basename(filename).encode())

                file_size = os.path.getsize(filename)
                ssl_socket.sendall(str(file_size).encode())
                # Send filename to the server
                
                with open(filename, 'rb') as file:
                    # Read and send file data in chunks
                    while True:
                        data = file.read(BUFFER_SIZE)
                        if not data:
                            break
                        ssl_socket.sendall(data)
                print("File uploaded successfully.")

                # Receive confirmation from the server
                confirmation = ssl_socket.recv(BUFFER_SIZE)
                if confirmation == b'Upload complete':
                    print("Upload confirmation received.")
                else:
                    print("Upload confirmation not received.")
    except Exception as e:
        print(f"Error uploading file '{filename}': {e}")

def download_file(filename):
    try:
        cert_path = os.path.join('certs', 'cert.pem')
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cert_path)
        with socket.create_connection((SERVER_HOST, SERVER_PORT)) as server_socket:
            with context.wrap_socket(server_socket, server_hostname=SERVER_HOST) as ssl_socket:
                # Send download command to the server
                ssl_socket.sendall(b'download')
                # Send filename to the server
                ssl_socket.sendall(os.path.basename(filename).encode())

                # Receive file size from the server
                file_size = int(ssl_socket.recv(BUFFER_SIZE).decode())
                
                # Specify absolute path for saving the downloaded file
                save_path = os.path.join(os.getcwd(), filename)
                
                # Receive file content from the server and save it
                with open(save_path, 'wb') as file:
                    received_size = 0
                    while received_size < file_size:
                        data = ssl_socket.recv(BUFFER_SIZE)
                        if not data:
                            break
                        file.write(data)
                        received_size += len(data)
                
                print(f"File '{filename}' downloaded successfully.")
    except Exception as e:
        print(f"Error downloading file '{filename}': {e}")

def main():
    print(logo)
    print("Connected to server.")

    while True:
        try:
            choice = input("Choose operation ('upload', 'download', or 'quit'): ").lower().strip()
            if choice == 'quit':
                break
            elif choice == 'upload':
                filename = input("Enter filename to upload: ").strip()
                if os.path.exists(filename):
                    upload_file(filename)
                else:
                    print("File not found. Please enter a valid filename.")
            elif choice == 'download':
                filename = input("Enter filename to download: ").strip()
                download_file(filename)
            else:
                print("Invalid choice.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()

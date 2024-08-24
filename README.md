# Secure File Transfer System 

This project is a client-server application designed for secure file transfer using SSL/TLS encryption. The server and client communicate over a secure connection, ensuring that files are transferred securely between them.

## Features

- **Secure Communication**: All communications between the client and server are encrypted using SSL/TLS.
- **File Upload/Download**: The client can upload files to the server or download files from the server.
- **Web Interface**: The server provides a simple web interface for file upload and download.
- **Configurable File Extensions**: The server restricts file uploads to specific file extensions.

## Requirements

- Python 3.x
- `Flask` for the web interface
- `Werkzeug` for handling file uploads securely
- `ssl` for secure communication

### Directory Structure

```plaintext
secure-file-transfer/
├── certs/
│   ├── cert.pem
│   └── key.pem
├── server_files/
│   └── # Directory where uploaded files will be stored
├── client.py
├── server.py
```

certs/: Directory containing SSL certificate and key files.
server_files/: Directory where files uploaded by the client are stored.
client.py: Client-side application for interacting with the server.
server.py: Server-side application that handles file uploads and downloads.


## Usage 

### Upload a File from the Client

1. Start the client using python client.py.
2. Enter upload when prompted.
3. Provide the path to the file you want to upload.
4. The file will be securely transferred to the server.

## Download a File to the Client


1. Start the client using python client.py.
2. Enter download when prompted.
3. Provide the filename you want to download.
4. The file will be securely transferred from the server to the client.



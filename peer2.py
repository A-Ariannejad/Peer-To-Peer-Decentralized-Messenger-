import copy
from io import StringIO
import socket
import threading
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

private_key = None
public_key = None

def generate_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key


def encrypt_message(public_key, message):
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(message)
    return ciphertext


def decrypt_message(private_key, ciphertext):
    key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(key)
    message = cipher.decrypt(ciphertext)
    return message




def handle_client(client_socket, client_address):
    while True:
        try:
            message = client_socket.recv(1024)
            m = decrypt_message(private_key.decode('utf-8'), message)
            if m:
                print(f"Received message from {client_address}: {m.decode('utf-8')}")
            else:
                clients.remove(client_socket)
                print(f"Client {client_address} has disconnected.")
                break
        except Exception as e:
            print(f"Error occurred for client {client_address}: {e}")
            break

def start_server():
    host = '127.0.0.1'  
    port = 5101

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((host, port))

    server_socket.listen(5)
    print("Server started, listening on port", port)

    while True:
        client_socket, client_address = server_socket.accept()
        print("Client connected:", client_address)
        
        t = client_socket.recv(1024).decode('utf-8')
        with open('cpk2.txt', 'w') as file:
            file.write(t)


        clients.append(client_socket)

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, ))
        client_thread.start()

def start_client():
    host = '127.0.0.1'  
    port = 5100

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((host, port))
        print("Connected to the server.")
        public_key_str = public_key.decode('utf-8')
        client_socket.send(public_key_str.encode('utf-8'))
        while True:
            time.sleep(1)
            with open('cpk2.txt', 'r') as file:
                client_public_key = file.read().encode('utf-8')

            message = input("Enter a message: ")
            m = encrypt_message(client_public_key, message.encode('utf-8'))
            client_socket.send(m)
    except Exception as e:
        print("Error occurred while connecting to the server:", e)
        start_client()
        client_socket.close()

clients = []

######################################################################### RSA #############################################################################
private_key, public_key = generate_key_pair()
print(private_key, public_key)

##########################################################################################################################################################################

server_thread = threading.Thread(target=start_server)
server_thread.start()

start_client()





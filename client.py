import os, random, string, datetime
import json, socket, threading, argparse
from termcolor import colored
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode, b64decode
from Crypto.Random import get_random_bytes

class Client:
    def __init__(self, server, port, username):
        self.server = server
        self.port = port
        self.username = username

## Create the connection to the server
    def create_connection(self):
## Setting up the socket
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.s.connect((self.server, self.port))
        except Exception as e:
            print(colored('[!] '+ e, 'red'))


        
        self.s.send(self.username.encode()) 
        print(colored('[+] Connected successfully', 'yellow'))
        print(colored('[+] Exchanging keys', 'yellow'))
        
        self.create_key_pairs()             
        self.exchange_public_keys()       
        global secret_key                  
        secret_key = self.handle_secret()  
        
        print(colored('[+] Initial set up had been completed!', 'yellow'))
        print(colored('[+] Now you can start to exchange messages', 'yellow'))

## InputHandle for sending messages and MessageHandle thread for receiving messages
        message_handler = threading.Thread(target=self.handle_messages,args=())
        message_handler.start()
        input_handler = threading.Thread(target=self.input_handler,args=())
        input_handler.start()

## Handle receiving messages
    def handle_messages(self):
        while True:
            message = self.s.recv(1024).decode()
            if message:
                key = secret_key           
                decrypt_message = json.loads(message)
                iv = b64decode(decrypt_message['iv'])           
                cipherText = b64decode(decrypt_message['ciphertext'])
                cipher = AES.new(key, AES.MODE_CFB, iv=iv)
                msg = cipher.decrypt(cipherText)                       
                current_time = datetime.datetime.now()
                print(colored(current_time.strftime('%Y-%m-%d %H:%M:%S ')+msg.decode(), 'green'))
            else:
                print(colored('[!] Lost the connection to the server', 'red'))
                print(colored('[!] Closing down the connection', 'red'))
                self.s.shutdown(socket.SHUT_RDWR)
                os._exit(0)

## Handle user input and send message
    def input_handler(self):
        while True:
            message = input()
            if message == "EXIT": 
                break
            else:
                key = secret_key
                cipher = AES.new(key, AES.MODE_CFB) 
                message_to_encrypt = self.username + ": " + message 
                msgBytes = message_to_encrypt.encode()
                encrypted_message = cipher.encrypt(msgBytes)
                iv = b64encode(cipher.iv).decode('utf-8') 
                message = b64encode(encrypted_message).decode('utf-8') 
                result = json.dumps({'iv':iv, 'ciphertext':message})
                self.s.send(result.encode())
        
        self.s.shutdown(socket.SHUT_RDWR)
        os._exit(0)

## Receiving the secret key for symmetric encryption
    def handle_secret(self):
            secret_key = self.s.recv(1024)
            private_key = RSA.importKey(open('client_private_key.pem', 'r').read()) 
            cipher = PKCS1_OAEP.new(private_key)
            return cipher.decrypt(secret_key)

## Send the public key to the server to encrypt the secret and the secret is generated by the server and used for symmetric encryption
    def exchange_public_keys(self):
        try:
            print(colored('[+] Getting public key from the server', 'blue'))
            server_public_key = self.s.recv(1024).decode()
            server_public_key = RSA.importKey(server_public_key)    

            print(colored('[+] Sending public key to server', 'blue'))
            public_pem_key = RSA.importKey(open('client_public_key.pem', 'r').read())
            self.s.send(public_pem_key.exportKey())
            print(colored('[+] Exchange completed!', 'yellow'))

        except Exception as e:
            print(colored('[!] ERROR, you messed up something.... '+e, 'red'))

## Generate public and private key pairs
    def create_key_pairs(self):
        try:    
            private_key = RSA.generate(2048)
            public_key = private_key.publickey()
            private_pem = private_key.exportKey().decode()
            public_pem = public_key.exportKey().decode()
            with open('client_private_key.pem', 'w') as priv:
                priv.write(private_pem)
            with open('client_public_key.pem', 'w') as pub:
                pub.write(public_pem)

        except Exception as e:
            print(colored('[!] ERROR, you messed up somethig.... '+e, 'red'))


if __name__ == "__main__":

## command line Arguments
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('-s', '--server', required=True, help="server ip to connect")
    arg_parse.add_argument('-p', '--port', required=True, type=int, help="port the server listening on")
    arg_parse.add_argument('-u', '--username', required=True, help="username of the user")
    args = arg_parse.parse_args()
    client = Client(args.server, args.port, args.username)
    client.create_connection()
    
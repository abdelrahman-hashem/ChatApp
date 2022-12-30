# ChatApp
Secure python chatting application
Summary
This chatting application will help two or more users communicate securely and freely by sending and receiving text messages. Data protection is everyone’s concern these days due to cyber-attacks in today’s digital world, as people want their shared files and messages to be secured from outsiders, this web chatting application provides both, asymmetric and symmetric encryption to avoid several types of attacks. The application should provide users with the highest level of privacy and security. The aim of this project is to apply cryptography methods for higher security.
  
  Usage
First install the implemented modules: RSA, Pycryptodome and termcolor with these commands
pip install rsa
pip install pycryptodome
pip install termcolor
Running the server: one parameter, (-p) port number 
Example: python3 server.py -p 4444
Client: three parameters, (-s) server IP, (-p) port number, (-u) username
Example: python3 client.py -s 127.0.0.1 -p 4444 -u Abdelrahman
Quitting server: 
TERMINATE 
quitting as a user:
EXIT

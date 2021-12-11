from logging import log
import socket
import threading
import time

from globals import *
from handle_req import *

#Server Params
SERVER_IP = "localhost"
SERVER_PORT = 1276


# Create Socket and Bind it
soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
soc.bind((SERVER_IP,SERVER_PORT))

# Listen for the requests
soc.listen()

logging.info("Server is running and listening on port "+str(SERVER_PORT))

# Blocking loop to accept the requests
while 1:
    conn, addr = soc.accept() 
    # Dispatch the connc socket to a thread
    clt_th = threading.Thread(target=handle_req,args=(conn,))
    clt_th.start()
    

    

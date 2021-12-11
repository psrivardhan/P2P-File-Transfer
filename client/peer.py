import socket
import curses
import curses.textpad
import pickle
import threading
import traceback
import os

from tui import *
from handlers import *
from time import sleep
from File import File
from globals import *



SERVER_IP = "localhost"
SERVER_PORT = 1276


class client:
    def __init__(self) -> None:
        files_available = {}
    
    # Connect server
    def connect_server(self):
        # Tries to connect to server
        # If failed retries again after 1 sec for 10 times
        for i in range(4):
            try:
                tui_set_server_status("Connecting...")  

                # Create A socket with timeout
                soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                soc.settimeout(3)
                soc.connect((SERVER_IP,SERVER_PORT))

                # Connection Succeded store the socket
                self.soc = soc
                tui_set_server_status("Connected",curses.color_pair(2))
                tui_set_clt_status(soc.getsockname())
                tui_log("Connected to central-server at "+str(SERVER_IP)+":"+str(SERVER_PORT)+"\n")
                self.bind_upstream_sockets()
                return
            except Exception as e:
                tui_set_server_status("Retrying...")
                tui_log("Problem connecting to server retrying again in 2sec\n")
                tui_log(str(e)+traceback.format_exc(),True)
                sleep(1.5)
                continue
        tui_set_server_status("Not-Connected",curses.color_pair(3))
        tui_log("Cannot connect to server... Relaunch the program or consider checking the server address")
        
        
        
    # Register a file with server

    def register_file(self,fileName):
        try:
            file_p = open(fileName,mode='rb')
            file = File(fileName,file_p)
            file.chunks_needed = []

            # Add to client maintained fileslist
            files_available[fileName] = file
            
            # Serialise this file object and send over socket to centalised server

            # Protocol
            self.soc.send(str(1).encode('utf8'))      
            payload = pickle.dumps(file)
            send_payload(self.soc,payload)

            tui_log("Metadata for file \""+fileName+"\" sent to server\n")

        except Exception as e:
            tui_log("File Not Registered: "+str(e)+"\n"+traceback.format_exc(),True)

    
    # Send the available chunk for a file 

    def notify_chunk_available(self,chunkno,filename):
        try:
            # Protocol
            self.soc.send(str(6).encode('utf8')) 

            # Send the filename
            payload = filename.encode('utf-8')
            send_payload(self.soc,payload)

            # Send the chunk number
            self.soc.send(chunkno.to_bytes(4,'little'))
        except Exception as e:
            tui_log(str(e)+"\n"+traceback.format_exc(),True)



    # Gets the list of all files available at server
    
    def get_files(self):
        try:
            # Protocol
            self.soc.send(str(2).encode('utf8'))  
            payload = recv_payload(self.soc)

            # Here payload is list of filenames
            fileList = pickle.loads(payload)
            tui_log("List of available files retrived from server\n")
            return fileList
        except Exception as e:
            tui_log("Unable to retrive files from server "+str(e)+traceback.format_exc(),True)
            return None
        
    
    # Gets all the metadata of the file 
    # Like checksums and size inforamtion etc.

    def get_file_instance_and_add(self,choosen_file):

        file = self.get_file_instance(choosen_file)
        
        # Handle the case where no such file exsist
        if file is None:
            tui_log(choosen_file+" No such file exist\n",True)
            return

        # Save this file object 
        file.chunks_needed = [i for i in range(file.total_chunks)]
        files_available[choosen_file] = file
        

    def get_file_instance(self,choosen_file):
        try:
            # Protocol
            self.soc.send(str(3).encode('utf8'))  

            # Send the file name to server
            payload = str(choosen_file).encode('utf-8')
            send_payload(self.soc ,payload)
            
            # Recive the file instance

            payload = recv_payload(self.soc)
            # Here Payload is file object
            
            file = pickle.loads(payload)
            assert isinstance(file,File)
           
            tui_log("Latest file Information for \""+choosen_file+"\" recieved from server\n")
            return file
            
        except Exception as e:
            tui_log(str(e)+traceback.format_exc(),True) 


        return None


    ## UpStream Sockets to bind
    def bind_upstream_sockets(self):

        self.upstream_sockets = []

        for i in range(3):
            try:
                soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                # Let os assign the free sockets
                soc.bind(('localhost',0))
                soc.listen()
                # Add to list of maintained sockets
                self.upstream_sockets.append(soc.getsockname())
                # Dispatch handling of each socket to a thread
                soc_thread = threading.Thread(target=handle_upstream_socket,args=(soc,))
                soc_thread.start()
            except Exception as e:
                tui_log("Error opening upstream sockets"+str(e)+traceback.format_exc(),True)
        
        tui_log("Upstream sockets opened: "+str(self.upstream_sockets)+"\n")
        # Send the list of upstream sockets ports to central server

        # Protocol
        self.soc.send(str(4).encode('utf8'))  

        payload = pickle.dumps(self.upstream_sockets)
        send_payload(self.soc,payload)
        tui_log("List of sockets exposed for upstream sent to server\n")






#########################################################

def main(stdscr):
    # Get screen width/height
    H,W= screen.getmaxyx()

    clt = client()
    ## Connect to the server
    clt.connect_server()
    

    ## Read the input from the terminal and perform actions
    while True:
        
        opt = inpbar.getch()

        resize = curses.is_term_resized(H,W)

        # Action in loop if resize is True:
        if resize is True:
            H,W = screen.getmaxyx()
            tui_handle_resize()
        
        if opt==ord('R') or opt==ord('r'):
            fileName = opt_get_filename()
            clt.register_file(fileName)
            tui_show_output("")
        
        elif opt== ord('D') or opt == ord('d'):
            opt_download_file(clt)

        elif opt == curses.KEY_DOWN:
            tui_log_scroll_down()
        
        elif opt == curses.KEY_UP:
            tui_log_scroll_up()

        elif opt == ord('q') or opt == ord('Q'):
            # Exit the program
            curses.curs_set(0)
            curses.echo()
            curses.endwin() 
            os._exit(1)

        tui_reset_bottom()
    
    


wrapper(main)

#################################################################

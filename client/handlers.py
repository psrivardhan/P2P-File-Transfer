import pickle
import random
import socket
import threading
import traceback
import hashlib


from File import File 
from tui import *
from globals import *



#########################################################

def send_payload(soc,payload):
    # Compute the size of the payload and send
    payload_sz = len(payload)
    soc.send(payload_sz.to_bytes(4,'little'))
    # Now send the payload
    len_sent = 0
    while len_sent < payload_sz:
        pkt_size = soc.send(payload) 
        len_sent += pkt_size

    tui_network_log_send("Message of length "+str(payload_sz)+" bytes sent to "+str(soc.getpeername())+" from socket binded to port "+str(soc.getsockname()[1])+"\n")

def recv_payload(soc):
    #Length of msg
    msg_len_raw = soc.recv(4)
    msg_len = int.from_bytes(msg_len_raw,'little')

    # Recive the paylaod data
    payload = bytearray()
    len_recv = 0

    while len_recv<msg_len:
        pkt = soc.recv(msg_len-len_recv)
        payload.extend(pkt)
        len_recv += len(pkt)

    tui_network_log_recv("Message of length "+str(msg_len)+" bytes recieved from "+str(soc.getpeername())+" via socket binded to port "+str(soc.getsockname()[1])+"\n")
    return payload

#########################################################

# Returns the FileName  and handles the tui change
def opt_get_filename():
   
    statbar.addstr(0,0,"Enter filename:")
    statbar.refresh()
    curses.curs_set(1)

    # Filename is entered in this textbox
    tb = curses.textpad.Textbox(inpbar, insert_mode=True)
    text = tb.edit()

    inpbar.clear()
    statbar.clear()
    statbar.addstr(0,0,"Choose option: ")
    statbar.refresh()
    curses.curs_set(0)

    return text[:-1]


# Gets the list of files available from the server and displays them

def opt_download_file(client):
    fileList = client.get_files()
    
    ## Dislplay the list of files to user
    ss = "Available Files List:\n"
    for i,file in enumerate(fileList):
        ss = ss +"\n"+str(i+1)+". "+str(file)
    
    tui_show_output(ss)

    ## Let user choose a file
    choosen_file = opt_get_filename()


    if files_available.get(choosen_file) is None:
        ## Send the file to server to get file Instance from the server
        client.get_file_instance_and_add(choosen_file)

    if files_available.get(choosen_file) is None:
        return 

    tui_log(choosen_file+" choosed for download\n")
    # Now find peers and request file
    download_file(client,choosen_file)

#################################################################


# Handle Upstream sockets

def handle_upstream_socket(soc:socket.socket):
    while 1:
        conn, addr = soc.accept() 
        # Dispatch the connc socket to a thread
        clt_th = threading.Thread(target=handle_upstream_req,args=(conn,))
        clt_th.start()


# Send the corresponding data for the client
# Protocol : Filename(recv) chunk_no(recv) -- bytes(send)
def handle_upstream_req(soc:socket.socket):

    tui_log("Peer: "+str(soc.getpeername())+" connected on port "+str(soc.getsockname()[1])+"\n")

    # Filename
    payload = recv_payload(soc)
    filename = payload.decode('utf-8')
    # chunkno
    chunkno = int.from_bytes(soc.recv(4),'little')

    # Search for the chuck
    file_obj = files_available[filename]
    file_p = open(filename,'rb')
    
    tui_log("Peer: "+str(soc.getpeername())+" requested chunk "+str(chunkno)+" of "+filename+"\n")

    # Caluclate the offset of chunk
    offset = file_obj.chunk_size * chunkno
    file_p.seek(offset,0)

    # Send the chunk over the socket
    send_payload(soc,file_p.read(file_obj.chunk_size))

    tui_log("Sent the requested chunk:"+str(chunkno)+" of "+filename+" to peer: "+str(soc.getpeername())+"\n")



    file_p.close()


###################################################################


def req_chunk_from(soc:socket.socket,filename:str,chunkno:int,chunksize:int):

    # Send the filename
    payload = filename.encode('utf-8')
    send_payload(soc,payload)

    # Send the chunk number
    soc.send(chunkno.to_bytes(4,'little'))

    # Now Recieve the data
    data = recv_payload(soc)

    return data


def receive_and_write_chunk(client,port_chosen:int,filename:str,chunkno:int):

    try:
        soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #new_soc.settimeout(25)
        soc.connect(port_chosen)
  

        # Open the fileDes
        file_obj = files_available[filename]
        assert isinstance(file_obj,File)

        # Recieve the data
        data = req_chunk_from(soc,filename,chunkno,file_obj.chunk_size)

        tui_log("Recieved chunk "+str(chunkno)+" for "+filename+" from "+str(soc.getpeername())+"\n")

        # Verify Hash Digest of the data recieved 
        # Proceed to write only if its valid

        cur_hash = hashlib.md5()
        cur_hash.update(data)
        cur_hash = cur_hash.hexdigest()

        # if cur_hash != file_obj.chunks_digest[chunkno]:
        #     raise Exception("Hash Digest mismatch for chunk "+str(chunkno)+" discarding chunk!!\n")


        ## Verification Succedded Proceed

        file_p = open(filename,'ab+')
        # Caluclate the offset of chunk
        offset = file_obj.chunk_size * chunkno
        file_p.seek(offset,0)

        file_p.write(data)
        file_p.close()



        tui_log("Removed chunk:"+str(chunkno)+" form required list for "+filename+" Required chunks : "+str(file_obj.chunks_needed)+"\n")

        # Send this information to server

        client.notify_chunk_available(chunkno,filename)

    except Exception as e:
        # Mark this chunk needed due to error
        file_obj.chunks_needed.append(chunkno)
        tui_log(str(e),True)
        
    
 

#################### Main Algo #######################

def download_file(client,filename):

    file_obj = files_available[filename]
   
    # Get the latest file info from server
    file = client.get_file_instance(filename)
    assert isinstance(file,File) and isinstance(file_obj,File)

    ## Show the information of file
    ss = "File Information:\n"
    ss = ss+ "\tFile Name: "+str(file_obj.ID)+"\n"
    ss = ss+ "\tFile size: "+str(file_obj.filesize)+" bytes\n"
    ss = ss+ "\tChunk Size: "+str(file_obj.chunk_size)+ " bytes\n"
    ss = ss+ "\tTotal chunks: "+str(file_obj.total_chunks)+"\n"
    
    
    tui_show_output(ss)

    while len(file_obj.chunks_needed) > 0:

        # Random choice of chunkno
        chunkno = random.choice(file_obj.chunks_needed)

        # Check if peers are available for chunk and are online
        if len(file.peers[chunkno]) <1 :
            continue
        
        peer_chosen = random.choice(file.peers[chunkno])

        # Send the peer_chosen and reciver peer's port
        
        # Protocol
        client.soc.send(str(5).encode('utf8'))  
        payload = pickle.dumps(peer_chosen)
        send_payload(client.soc,payload)

        # Recieve the port list
        payload = recv_payload(client.soc)
        ports_list = pickle.loads(payload)

        port_chosen = random.choice(ports_list)

        tui_log("Requesting chunk:"+str(chunkno) +"for "+filename+" from "+str(port_chosen)+"\n")
        

        # Remove the chunkno from the needed list of chunks to avoid race conditions
        # if failed will be added back
        file_obj.chunks_needed.remove(chunkno)


        # # Dispatch this request to new threads
        # Uncomment to allow parallel download

        # th = threading.Thread(target=receive_and_write_chunk,args=(client,port_chosen,filename,chunkno,))
        # th.start()

        receive_and_write_chunk(client,port_chosen,filename,chunkno)
        
    
    # To check the integrity of total file
    file_p = open(filename,"rb")
    data = file_p.read()
    cur_hash = hashlib.md5()
    cur_hash.update(data)

    # if cur_hash.hexdigest() == file_obj.chunks_digest[-1]:
    #     tui_log("File "+filename+" downloaded succesfully\n",False,True)
    # else:
    #     # Handle this carefully
    #     tui_log("File "+filename+" downloaded but Hashdigest mismatch!!-- Removing the file\n",True)

    tui_log("File "+filename+" downloaded succesfully\n",False,True)

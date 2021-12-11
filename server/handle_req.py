import socket
import pickle

from File import File 
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

    logging.debug("Message of length "+str(payload_sz)+" bytes sent to "+str(soc.getpeername())+" from socket binded to port "+str(soc.getsockname()[1])+"\n")

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

    logging.debug("Message of length "+str(msg_len)+" bytes recieved from "+str(soc.getpeername())+" via socket binded to port "+str(soc.getsockname()[1])+"\n")
    return payload

#########################################################

def handle_req(soc : socket.socket):

    peers_online.append(soc.getpeername())
    logging.info("Peer: "+str(soc.getpeername())+"Connected")
    while 1:
        # Recieve the operation code
        op_raw = soc.recv(1)
        # Exit if client disconnected from server
        if op_raw == b'':
            # Clean the all the data
            peers_online.remove(soc.getpeername())
            #upstream_ports.pop(soc.getpeername())
            logging.critical("Peer: "+soc.getpeername()+" disconnected")
            return
        opcode = int(op_raw.decode('utf8'))

        logging.info("opcode: "+str(opcode)+" recieved from "+str(soc.getpeername()))

        

        
        # Register a file

        if opcode==1: 
            payload = recv_payload(soc)

            # Payload is file object
            file = pickle.loads(payload)
            assert isinstance(file,File)

            # Add the file to list
            files_available[file.ID] = file

            # Add the current peer to all chunks
            file.add_peer_to_all_chunks(soc.getpeername())

            logging.info("File registerd: "+file.ID)

        # Send the list of all avaliable files
        elif opcode==2:

            # Serialse the list of files
            payload = pickle.dumps(list(files_available.keys()))
            send_payload(soc,payload)

            logging.info("Sending the list of files to "+str(soc.getpeername()))

        # Send the requested file object
        elif opcode == 3:

            payload = recv_payload(soc)
            file_chosen = payload.decode('utf-8')

            
            # Now send the file instance
            payload = pickle.dumps(files_available.get(file_chosen))
            send_payload(soc,payload)

            logging.info("Sending the latest file info for "+file_chosen+" to "+str(soc.getpeername()))

        # Recieve the peer--upstream ports information
        elif opcode == 4:
            
            payload = recv_payload(soc)
            ports_list = pickle.loads(payload)

            upstream_ports[soc.getpeername()] = ports_list

            logging.info("Recieved the list of ports exposed by "+str(soc.getpeername()))
            
        # Send the upstream ports list requested peer
        
        elif opcode == 5:

            payload = recv_payload(soc)
            req_peer = pickle.loads(payload)

            # Return the list of all ports exposed

            ports_list = upstream_ports.get(req_peer) if req_peer in peers_online else []
            payload = pickle.dumps(ports_list)
            send_payload(soc,payload)

            logging.info("Sending the list of ports exposed by "+str(req_peer))

        # Updated peers list for chunk of a file

        elif opcode == 6:

            # Get filename and chunkno
            # Filename
            payload = recv_payload(soc)
            filename = payload.decode('utf-8')
            # chunkno
            chunkno = int.from_bytes(soc.recv(4),'little')

            # Update it in peer's list of the file
            files_available[filename].add_peer_with_chunk(soc.getpeername(),chunkno)

            logging.info("Added peer  "+str(req_peer)+" to chunk "+str(chunkno)+" for file "+filename)

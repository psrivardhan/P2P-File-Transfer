import hashlib
import os
from socket import socket

class File:
    # Unique-ID : filename
    def __init__(self,fileName,file) -> None:
        self.chunk_size = 524288 # 512KB
        self.ID = fileName
        # Compute the hashes
        self.compute_chunks(file)
        self.filesize = os.path.getsize(fileName)
        

        

    def compute_chunks(self,file):
        chunks_digest=[]
        total_hash = hashlib.md5()
        for chunk in iter(lambda: file.read(self.chunk_size), b""):
            # Append the hash of current chunk also
            cur_hash = hashlib.md5()
            cur_hash.update(chunk)
            chunks_digest.append(cur_hash.hexdigest())
            total_hash.update(chunk)
        # Total chunks
        self.total_chunks = len(chunks_digest)
        # Append the total hash to check the chunk ordering
        chunks_digest.append(total_hash.hexdigest())
        self.chunks_digest = chunks_digest
        # Peer list for each chunk
        self.peers = [[] for i in range(self.total_chunks)]
        
    def get_peers_with_chunk(self,chunk_id):
        return self.peers[chunk_id]

    def add_peer_with_chunk(self,peer,chunk_id):
        self.peers[chunk_id].append(peer)

    def add_peer_to_all_chunks(self,peer):
        for i in range(self.total_chunks):
            self.peers[i].append(peer) 

    

class HashMisMatchException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
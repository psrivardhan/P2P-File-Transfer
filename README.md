# Quick Transfer -- P2P File transfer
---

## Team :

* P SRIVARDHAN    ----    CS19BTECH11052
* K RITHVIK       ----    CS19BTECH11038
* A MAHIDHAR      ----    CS19BTECH11046
* V NIKHILESH	  ----    ES19BTECH11030
* M SHATHANAND    ----    CS19BTECH11005
* T ESHWAR        ----     CS19BTECH11040


## Description

![Image](http://teaching.idallen.com/cst8165/07w/notes/kurose/.slide_kurose_320719_c02f23.gif)

This a implementation of Centralised - Peer-to-Peer file transfer. All the information of a files to are in the central server. For the file transfer the peer quries the servers for the list of peers containing the file (Chunk) already.

### Source Code Info:
Client folder -- All the code related to peers
 - tui.py -- Handling of textual user interface
 - handlers.py -- Functions doing the work
 - peer.py -- Implementation of peer
 - File.py -- File object represting the file metadata

Server folder -- Code for the centralised server
 - central_server.py -- Implemntation of central_Server
 - handle_req.py -- Functions doing the work
 - File.py -- File object represting the file metadata




## References

* [Python Docs Sockets](https://docs.python.org/3/library/socket.html)
* [Python howto Docs](https://docs.python.org/3/howto/sockets.html)
* [Python Docs Curses](https://docs.python.org/3/howto/curses.html)
* Varies questions on stackoverflow!!
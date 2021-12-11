import logging
import sys



root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%I:%M:%S %p')
handler.setFormatter(formatter)
root.addHandler(handler)

# Stores the list of peers that are connected to server
peers_online = []
# Stores the list of files than are available as dict
files_available = {}
# Stores the list of upstream ports exposed by each peer as dict
upstream_ports = {}
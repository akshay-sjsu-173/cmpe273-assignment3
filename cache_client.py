import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
from decorators import lru_cache

BUFFER_SIZE = 1024

class UDPClient():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)       

    def send(self, request):
        print('Connecting to server at {}:{}'.format(self.host, self.port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (self.host, self.port))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()

@lru_cache
def add(u, client_ring, hash_codes):
    data_bytes, key = serialize_PUT(u)
    response = client_ring.get_node(key).send(data_bytes)
    return response

@lru_cache
def get(hc, client_ring, hash_codes):
    data_bytes, key = serialize_GET(hc)
    response = client_ring.get_node(key).send(data_bytes)
    return response

@lru_cache
def delete(hc, client_ring, hash_codes):
    data_bytes, key = serialize_DELETE(hc)
    response = client_ring.get_node(key).send(data_bytes)
    return response

def process(udp_clients):
    client_ring = NodeRing(udp_clients)
    hash_codes = set()
    # PUT all users.
    for u in USERS:
        response = add(u, client_ring, hash_codes)
        print(response)
        hash_codes.add(str(response.decode()))
        #print(len(hash_codes))

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")
    
    # GET all users.
    for hc in list(hash_codes)[::2]:
        response = get(hc, client_ring, hash_codes)
        print(response)

    # DELETE all users
    for hc in hash_codes:
        response = delete(hc, client_ring, hash_codes)
        print(response)

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)

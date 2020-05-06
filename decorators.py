from collections import OrderedDict as od
from datetime import datetime
import pickle,hashlib
#import pyhash

lru = {}
lru_cap = 5
bloomfilter = [False for i in range(4000000)]
bloom_size = len(bloomfilter)

#def bloom(func):
def is_member(hc):
    '''
    hash hc thrice and modulo len(bloomfilter)
    '''
    global bloomfilter, bloom_size
    print("Check membership for ",hc)
    for i in range(3):
        object_bytes = pickle.dumps(hc)
        hc = hashlib.md5(object_bytes).hexdigest()
        bloom_index = int(hc,16)%bloom_size
        if not bloomfilter[bloom_index]:
            return False
    return True

def add_member(hc):
    '''
    hash hc thrice and modulo len(bloomfilter)
    '''
    global bloomfilter, bloom_size
    print("Add ",hc," to bloom")
    for i in range(3):
        object_bytes = pickle.dumps(hc)
        hc = hashlib.md5(object_bytes).hexdigest()
        bloom_index = int(hc,16)%bloom_size
        bloomfilter[bloom_index] = True
    return True

def lru_cache(func):#*args, **kwargs):

    #@bloom
    def add(u, client_ring, hash_codes):
        global lru
        response = func(u, client_ring, hash_codes)
        if response:
            print("Add to Cache", response)
            if len(lru.keys()) < lru_cap:
                lru[str(response.decode())] = {"object": u, "time": datetime.now()}
            else:
                print("Delete least recently used key")
                ordered = od(sorted(lru.items(), key=lambda item: item[1]['time'], reverse=True))
                del lru[list(ordered.keys())[0]]
        else:
            print("Server respnded negatively. Not adding to cache")
        #make an entry to bloom filter
        print("Added to bloom : ",add_member(response))
        return response

    #@bloom
    def delete(hc, client_ring, hash_codes):
        if not is_member(hc.encode()):
            return "Invalid hash code"
        response = func(hc, client_ring, hash_codes)
        if response:
            print("Delete from Cache")
            if lru.get(hc):
                del lru[hc]
            else:
                print("Key not present in cache for deletion")
        else:
            print("Server respnded negatively. Not deleting from cache")
        return response
    
    #@bloom
    def get(hc, client_ring, hash_codes):
        if not is_member(hc.encode()):
            return "Invalid hash code"
        global lru
        print("Get from LRU . . .", hc)
        cacheResponse = lru.get(hc)
        #print(cacheResponse)
        if cacheResponse:
            lru[hc]['time'] = datetime.now()
            print("Returning from cache")
            return lru[hc]['object']
        else:
            print("Fetching from server")
            return func(hc, client_ring, hash_codes)
    
    switcher = {
        "add": add,
        "get": get,
        "delete": delete
    }
    return switcher[func.__name__]

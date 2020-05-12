import hashlib
import math
import pickle

class BloomFilter:
    
    #bloomfilter = [] #False for i in range(4000000)]
    #bloom_size = len(bloomfilter) 

    def __init__(self, num_keys, false_positive_probability):
        n = 1000000
        m = -int((n*math.log(false_positive_probability)/math.log(2)**2))
        k = int((m/n)*math.log(2))
        print(k,m,n)
        self.bloomfilter = [False for i in range(k)]
        self.bloom_size = len(self.bloomfilter)

    def is_member(self, hc):
        '''
        hash hc thrice and modulo len(bloomfilter)
        '''
        #global bloomfilter, bloom_size
        print("Check membership for ",hc)
        for i in range(3):
            object_bytes = pickle.dumps(hc)
            hc = hashlib.md5(object_bytes).hexdigest()
            bloom_index = int(hc,16)%self.bloom_size
            if not self.bloomfilter[bloom_index]:
                return False
        return True

    def add(self, hc):
        '''
        hash hc thrice and modulo len(bloomfilter)
        '''
        #global bloomfilter, bloom_size
        print("Add ",hc," to bloom")
        for i in range(3):
            object_bytes = pickle.dumps(hc)
            hc = hashlib.md5(object_bytes).hexdigest()
            bloom_index = int(hc,16)%self.bloom_size
            self.bloomfilter[bloom_index] = True
        return True

    #def add(key):
    #    print("Add to bloom")
    #def is_member(key):
    #    print("Check membership")


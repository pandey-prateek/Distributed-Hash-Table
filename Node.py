import hashlib
import DataStore
import FingerTable
import RequestHandler
class Node(object):
    def __init__(self,ip,port,m=7):
        self.ip=ip
        self.port=int(port)
        self.id = self.hash(self.__str__())
        self.predecessor=None
        self.successor =None
        self.m=m
        self.dataStore=DataStore()
        self.fingerTable = FingerTable(self.id)
        self.requestHandle = RequestHandler()
        
    def hash(self,message):
        digest=hashlib.sha256(message.encode()).hexdigest()
        digest=int(digest,16) % pow(2,self.m)
        
    def __str__(self):
        return str({"ip":self.ip,"port":self.port})

    def find_successor(self, id):
        p = self.find_predecessor(id)
        return p.successor
    
    def find_predecessor(self, id):
        n = self.id
        while not(n < id <= n.successor):
            n = n.closest_preceding_finger(id)
        return n
    
    def closest_preceding_finger(self, id):
        for i in range(self.m, 0, -1):
            n = self.fingerTable.table[i-1][1]
            if self.id < n.id < id:
                return n
        return self

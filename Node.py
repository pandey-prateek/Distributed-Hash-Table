import hashlib
from DataStore import DataStore
from FingerTable import FingerTable

class Node(object):
    def __init__(self,ip,port,m=7):
        self.ip=ip
        self.port=int(port)
        self.predecessor=None
        self.successor =None
        self.m=m
        self.id = self.hash(self.__str__())
        self.dataStore=DataStore()
        self.fingerTable = FingerTable(self.id,self)
        
    def hash(self,message):
        digest=hashlib.sha256(message.encode()).hexdigest()
        digest=int(digest,16) % pow(2,self.m)
        return digest
        
    def __str__(self):
        return str(self.ip+"|"+str(self.port))

    def get_successor(self):
        if self.successor is None:
            return "None"
        return self.successor.__str__()
    
    def get_predecessor(self):
        if self.predecessor is None:
            return "None"
        return self.predecessor.__str__()
    
    def get_id(self):
        return str(self.id)
    
from Node import Node
import time
from RequestHandler import RequestHandler
import random
import threading


class HandleNode(object):
    
    def __init__(self,m=7,node=Node("0.0.0.0",1234)) -> None:
        self.node=node
        self.m=m
        self.requestHandler = RequestHandler()
    def process_requests(self,message):
        messages = message.split('|')
        operation = messages[0]
        args = []
        if len(messages) > 1 :
            args=messages[1:]
        result = "Done"
        if operation == 'insert_server' :
            data = messages[1].split(":")
            self.node.dataStore.insert(key=data[0],value=data[1])
            result = "Inserted"
            
            
        if operation == 'delete_server' :
            data = messages[1].split(":")
            self.node.dataStore.delete(key=data)
            result = "Deleted"
            
        if operation == 'search_server' :
            data = messages[1].split(":")
            val = self.node.dataStore.search(key=data)
            if val is None:
                return "Key Not Found"
            return val
        
        if operation == 'insert' :
            data = messages[1].split(":")
            self.node.dataStore.insert(key=data[0],value=data[1])
            result = "Inserted"
            
    def match(self,node):
        return node.ip == self.node.ip  and self.node.port == node.port
    
    
    def getIpPort(self,msg):
        msg=msg.strip().split('|')
        return msg[0] , int(msg[1])    
    
    def getBackwardDistance(self, node):
        
        if(self.node.id > node):
            return self.node.id - node
        elif self.id == node:
            return 0
        return pow(2,self.m) - abs(self.node.id - node)
        

    def getBackwardDistance2nodes(self, node2, node1):
        
        if(node2 > node1):
            return node2 - node1
        elif node2 == node1:
            return 0
        else:
            return pow(2,self.m) - abs(node2 - node1)
        

    def getForwardDistance(self,node):
        return pow(2,self.m) - self.getBackwardDistance(node)


    def getForwardDistance2nodes(self,node2,node1):
        return pow(2,self.m) - self.getBackwardDistance2nodes(node2,node1)
    
        
    def stabilize(self):
        
        while True:
            if (self.node.successor is None ) or self.match(self.node.successor):
                time.sleep(10)
                continue
            data = "get_predecessor"
            result = self.requestHandler.send_message(self.node.successor.ip , self.node.successor.port , data)
            if result == "None" or len(result) == 0:
                self.requestHandler.send_message(self.node.successor.ip , self.node.successor.port, "notify|"+ str(self.node.id) + "|" + self.node.__str__())
                continue

            ip , port = self.getIpPort(result)
            result = int(self.requestHandler.send_message(ip,port,"get_id"))
            if self.getBackwardDistance(result) > self.getBackwardDistance(self.node.successor.id):
                self.successor = Node(ip,port)
                self.node.fingerTable.table[0][1] = self.node.successor
            self.requestHandler.send_message(self.node.successor.ip , self.node.successor.port, "notify|"+ str(self.node.id) + "|" + self.node.__str__())
            print("===============================================")
            print("STABILIZING")
            print("===============================================")
            print("ID: ", self.node.id)
            if self.node.successor is not None:
                print("Successor ID: " , self.node.successor.id)
            if self.node.predecessor is not None:
                print("predecessor ID: " , self.node.predecessor.id)
            print("===============================================")
            print("=============== FINGER TABLE ==================")
            self.node.fingerTable.get_entry()
            print("===============================================")
            print("DATA STORE")
            print("===============================================")
            print(str(self.node.dataStore.data))
            print("===============================================")
            print("+++++++++++++++ END +++++++++++++++++++++++++++")
            print()
            print()
            print()
            time.sleep(10)
    def fixFingers(self):

        while True:

            random_index = random.randint(1,self.m-1)
            finger = self.node.fingerTable.table[random_index][0]
            data = self.node.find_predecessor(finger)
            if data == "None":
                time.sleep(10)
                continue
            ip,port = self.getIpPort(data)
            self.node.fingerTable.table[random_index][1] = Node(ip,port) 
            time.sleep(10)
            
    def start(self):
        
        thread_for_stabalize = threading.Thread(target = self.stabilize)
        thread_for_stabalize.start()
        thread_for_fix_finger = threading.Thread(target=  self.fix_fingers)
        thread_for_fix_finger.start()

        

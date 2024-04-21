from Node import Node
import time
from RequestHandler import RequestHandler
import random
import threading
import socket
import sys
from prettytable import PrettyTable

class HandleNode(object):
    
    def __init__(self,m=7,node=Node("0.0.0.0",1235)) -> None:
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
        
        if operation == "find_predecessor":
            # print("finding predecessor")
            result = self.find_predecessor(int(args[0]))

        if operation == "find_successor":
            # print("finding successor")
            result = self.find_successor(int(args[0]))

        if operation == "get_successor":
            # print("getting successor")
            result = self.node.get_successor()

        if operation == "get_predecessor":
            # print("getting predecessor")
            result = self.node.get_predecessor()

        if operation == "get_id":
            # print("getting id")
            result = self.node.get_id()

        if operation == "notify":
            # print("notifiying")
            self.notify(int(args[0]),args[1],args[2])
        
        if operation == "insert":
            # print("finding hop to insert the key" , str(self.nodeinfo) )
            data = message.split('|')[1].split(":") 
            key = data[0]
            value = data[1]
            result = self.insert_key(key,value)


        if operation == "delete":
            # print("finding hop to delete the key" , str(self.nodeinfo) )
            data = message.split('|')[1]
            result = self.delete_key(data)


        if operation == 'search':
            # print('Seaching...')
            data = message.split('|')[1]
            result = self.search_key(data)

        if operation == "send_keys":
            id_of_joining_node = int(args[0])
            result = self.send_keys(id_of_joining_node)

        if operation == "join_request":
            # print("join request recv")
            result  = self.join_request_from_other_node(int(args[0]))


        return str(result)
    

    def insert_key(self,key,value):
        '''
        The function to handle the incoming key_value pair insertion request from the client this function searches for the
        correct node on which the key_value pair needs to be stored and then sends a message to that node to store the 
        key_val pair in its data_store
        '''
        id_of_key = self.node.hash(str(key))
        succ = self.find_successor(id_of_key)
        # print("Succ found for inserting key" , id_of_key , succ)
        ip,port = self.getIpPort(succ)
        self.requestHandler.send_message(ip,port,"insert_server|" + str(key) + ":" + str(value) )
        return "Inserted at node id " + str(Node(ip,port).id) + " key was " + str(key) + " key hash was " + str(id_of_key)  

    def delete_key(self,key):
        '''
        The function to handle the incoming key_value pair deletion request from the client this function searches for the
        correct node on which the key_value pair is stored and then sends a message to that node to delete the key_val
        pair in its data_store.
        '''
        id_of_key = self.node.hash(str(key))
        succ = self.find_successor(id_of_key)
        # print("Succ found for deleting key" , id_of_key , succ)
        ip,port = self.getIpPort(succ)
        self.requestHandler.send_message(ip,port,"delete_server|" + str(key) )
        return "deleted at node id " + str(Node(ip,port).id) + " key was " + str(key) + " key hash was " + str(id_of_key)


    def search_key(self,key):
        '''
        The function to handle the incoming key_value pair search request from the client this function searches for the
        correct node on which the key_value pair is stored and then sends a message to that node to return the value 
        corresponding to that key.
        '''
        id_of_key = self.node.hash(str(key))
        succ = self.find_successor(id_of_key)
        # print("Succ found for searching key" , id_of_key , succ)
        ip,port = self.getIpPort(succ)
        data = self.requestHandler.send_message(ip,port,"search_server|" + str(key) )
        return data


    def notify(self, node_id , node_ip , node_port):
        '''
        Recevies notification from stabilized function when there is change in successor
        '''
        if self.node.predecessor is not None:
            if self.getBackwardDistance(node_id) < self.getBackwardDistance(self.node.predecessor.id):
                # print("someone notified me")
                # print("changing my pred", node_id)
                self.node.predecessor = Node(node_ip,int(node_port))
                return
        if self.node.predecessor is None or self.node.predecessor == "None" or ( node_id > self.node.predecessor.id and node_id < self.node.id ) or ( self.node.id == self.node.predecessor.id and node_id != self.node.id) :
            # print("someone notified me")
            # print("changing my pred", node_id)
            self.node.predecessor = Node(node_ip,int(node_port))
            if self.node.id == self.node.successor.id:
                # print("changing my succ", node_id)
                self.node.successor = Node(node_ip,int(node_port))
                self.node.fingerTable.table[0][1] = self.node.successor


    def join_request_from_other_node(self, node_id):
        """ will return successor for the node who is requesting to join """
        return self.find_successor(node_id)


    def serve_requests(self, conn, addr):
            '''
        The serve_requests fucntion is used to listen to incomint requests on the open port and then reply to them it 
        takes as arguments the connection and the address of the connected device. 
        '''
            with conn:
                
                data = conn.recv(1024)
                
                data = str(data.decode('utf-8'))
                data = data.strip('\n')
                # print(data)
                data = self.process_requests(data)
                # print('Sending', data)
                data = bytes(str(data), 'utf-8')
                conn.sendall(data)



    def join(self,node_ip, node_port):
        '''
        Function responsible to join any new nodes to the chord ring it finds out the successor and the predecessor of the
        new incoming node in the ring and then it sends a send_keys request to its successor to recieve all the keys 
        smaller than its id from its successor.
        '''

        data = 'join_request|' + str(self.node.id)
        succ = self.requestHandler.send_message(node_ip,node_port,data)
        ip,port = self.getIpPort(succ)
        self.node.successor = Node(ip,port)
        self.node.fingerTable.table[0][1] = self.node.successor
        self.node.predecessor = None
        
        if self.node.successor.id != self.node.id:
            data = self.requestHandler.send_message(self.node.successor.ip , self.node.successor.port, "send_keys|"+str(self.node.id))
            # print("data recieved" , data)
            for key_value in data.split(':'):
                if len(key_value) > 1:
                    # print(key_value.split('|'))
                    self.node.dataStore.data[key_value.split('|')[0]] = key_value.split('|')[1]

    def find_predecessor(self, search_id):
        
        if search_id == self.node.id:
            return str(self.node)
        # print("finding pred for id ", search_id)
        if self.node.predecessor is not None and  self.node.successor.id == self.node.id:
            return self.node.__str__()
        if self.getForwardDistance(self.node.successor.id) > self.getForwardDistance(search_id):
            return self.node.__str__()
        else:
            new_node_hop = self.closest_preceding_node(search_id)
            # print("new node hop finding hops in find predecessor" , new_node_hop.nodeinfo.__str__() )
            if new_node_hop is None:
                return "None"
            ip, port = self.getIpPort(new_node_hop.__str__())
            if ip == self.node.ip and port == self.node.port:
                return self.node.__str__()
            data = self.requestHandler.send_message(ip , port, "find_predecessor|"+str(search_id))
            return data

    def find_successor(self, search_id):
        
        if(search_id == self.node.id):
            return str(self.node)
        predecessor = self.find_predecessor(search_id)
        if(predecessor == "None"):
            return "None"
        ip,port = self.getIpPort(predecessor)
        print(ip,port)
        data = self.requestHandler.send_message(ip , port, "get_successor")
        return data
    
    def closest_preceding_node(self, search_id):
        closest_node = None
        min_distance = pow(2,self.m)+1
        for i in list(reversed(range(self.m))):
            # print("checking hops" ,i ,self.finger_table.table[i][1])
            if  self.node.fingerTable.table[i][1] is not None and self.getForwardDistance2nodes(self.node.fingerTable.table[i][1].id,search_id) < min_distance  :
                closest_node = self.node.fingerTable.table[i][1]
                min_distance = self.getForwardDistance2nodes(self.node.fingerTable.table[i][1].id,search_id)
                # print("Min distance",min_distance)

        return closest_node
    
    def match(self,node):
        return node.ip == self.node.ip  and self.node.port == node.port
    
    

    def getIpPort(self,msg):
        msg=msg.strip().split('|')
        print(msg,".......................................")
        return msg[0] , int(msg[1])    
    

    def getBackwardDistance(self, node):
        
        if(self.node.id > node):
            return self.node.id - node
        elif self.node.id == node:
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
                self.node.successor = Node(ip,port)
                self.node.fingerTable.table[0][1] = self.node.successor
            self.requestHandler.send_message(self.node.successor.ip , self.node.successor.port, "notify|"+ str(self.node.id) + "|" + self.node.__str__())
            # print("===============================================")
            # print("==============  STABILIZING  ==================")
            # print("===============================================")
            t = PrettyTable(['ID','Value'])
            t.title="STABILIZING"
            t.add_row(["Node iD: ", self.node.id])
            if self.node.successor is not None:
                t.add_row(["Successor ID: ", self.node.successor.id])
            else:
                t.add_row(["Successor ID: ", None])
            if self.node.predecessor is not None:
                t.add_row(["Predecessor ID: ", self.node.predecessor.id])
            else:
                t.add_row(["Predecessor ID: ", None])
            print(t)
            # print("===============================================")
            # print("=============== FINGER TABLE ==================")
            self.node.fingerTable.get_entry()
            # print("===============================================")
            # print("DATA STORE")
            # print("===============================================")
            self.node.dataStore.printdataStore()
            # print(str(self.node.dataStore.data))
            # print("===============================================")
            # print("+++++++++++++++ END +++++++++++++++++++++++++++")
            print()
            print()
            print()
            time.sleep(10)


    def send_keys(self, id_of_joining_node):

            data = ""
            keys_to_be_removed = []
            for keys in self.node.dataStore.data:
                key_id = self.node.hash(str(keys))
                if self.getForwardDistance2nodes(key_id , id_of_joining_node) < self.getForwardDistance2nodes(key_id,self.id):
                    data += str(keys) + "|" + str(self.node.dataStore.data[keys]) + ":"
                    keys_to_be_removed.append(keys)
            for keys in keys_to_be_removed:
                self.node.dataStore.data.pop(keys)
            return data
    

    def fixFingers(self):

        while True:

            random_index = random.randint(1,self.m-1)
            finger = self.node.fingerTable.table[random_index][0]
            data = self.find_successor(finger)
            if data == "None":
                time.sleep(10)
                continue
            ip,port = self.getIpPort(data)
            self.node.fingerTable.table[random_index][1] = Node(ip,port) 
            time.sleep(10)


    def start(self):
        
        thread_for_stabalize = threading.Thread(target = self.stabilize)
        thread_for_stabalize.start()
        thread_for_fix_finger = threading.Thread(target=  self.fixFingers)
        thread_for_fix_finger.start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.node.ip, self.node.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=self.serve_requests, args=(conn,addr))
                t.start()   
        

ip = "127.0.0.1"


if len(sys.argv) == 3:
    print("JOINING RING")
    node = Node(ip, int(sys.argv[1]))

    handle_node=HandleNode(7,node=node)

    handle_node.join(ip,int(sys.argv[2]))
    handle_node.start()

if len(sys.argv) == 2:
    print("CREATING RING")
    node = Node(ip, int(sys.argv[1]))

    handle_node=HandleNode(7,node=node)

    handle_node.node.predecessor = Node(ip,node.port)
    handle_node.node.successor = Node(ip,node.port)
    handle_node.node.fingerTable.table[0][1] = node
    
    handle_node.start()

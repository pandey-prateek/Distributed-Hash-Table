from Node import Node
class HandleNode(object):
    
    def __init__(self,m=7,node=Node("0.0.0.0",1234)) -> None:
        self.node=node
        self.m=m
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
        

class DataStore(object):
    
    def __init__(self) -> None:
        self.data={}
    def insert(self,key,value) -> None:
        self.data[key]=value
    def delete(self,key) -> None:
        if key in self.data:
            del self.data[key]
    def search(self,key):
        if key in self.data:
            return self.data[key]
        return None
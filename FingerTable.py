class FingerTable(object):
    def __init__(self,id,m=7) -> None:
        self.table=[[(id+pow(2,i))%pow(2,m),None] for i in range(m)]
    def get_entry(self):
        for _index,(entry,node) in enumerate(self.table):
            if node is None:
                print('Entry: ', _index, " Interval start: ", entry," Successor: ", "None")
            else:
                print('Entry: ', _index, " Interval start: ", entry," Successor: ", node.id)
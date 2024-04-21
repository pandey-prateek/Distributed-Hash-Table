from prettytable import PrettyTable
class FingerTable(object):
    def __init__(self,id,node,m=7) -> None:
        self.table=[[(id+pow(2,i))%pow(2,m),node] for i in range(m)]
    def get_entry(self):
        t = PrettyTable(['Entry', 'Interval start','Successor'])
        t.title="FINGER TABLE"
        for _index,(entry,node) in enumerate(self.table):
            if node is None:
                t.add_row([_index, entry,None])
            else:
                t.add_row([_index, entry,node.id])
        print(t)

import socket
from prettytable import PrettyTable

def main():
	#ip = input("Give the ip address of a node")
    ip = "127.0.0.1"
	#port = 9000
    port = int(input("Give the port number of a node "))
	
    while(True):
        t = PrettyTable(['Index', 'Command'])
        t.title="MENU"
        t.add_row(["1","Enter Key"])
        t.add_row(["2","Search Key"])
        t.add_row(["3","Delete Key"])
        t.add_row(["4","Exit"])
        
        print(t)
        choice = input(">> ")
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        sock.connect((ip,port))

        if(choice == '1'):
            key = input("KEY : ")
            val = input("VALUE : ")
            message = "insert|" + str(key) + ":" + str(val)
            sock.send(message.encode('utf-8'))
            data = sock.recv(1024)
            data = str(data.decode('utf-8'))
            print(data)

        elif(choice == '3'):
            key = input("ENTER THE KEY")
            message = "delete|" + str(key)
            sock.send(message.encode('utf-8'))
            data = sock.recv(1024)
            data = str(data.decode('utf-8'))
            print(data)
	
        elif(choice == '2'):
            key = input("ENTER THE KEY")
            message = "search|" + str(key)
            sock.send(message.encode('utf-8'))
            data = sock.recv(1024)
            data = str(data.decode('utf-8'))
            print("The value corresponding to the key is : ",data)

		

        elif(choice == '4'):
            print("Closing the socket")
            sock.close()
            print("Exiting Client")
            exit()
			
        else:
            print("INCORRECT CHOICE")



if __name__ == '__main__':
	main()

import socket
import datetime
import time


HEADER = 8
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "exit"
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)


def check_connection(ADDR):
    print("Trying to connect to the server...")
    connected = False
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while not connected:
        try:
            client.connect(ADDR)        
        except socket.error as error:
            connected = False
            time.sleep(0.01)
            print("Can't connect.Retrying...")
            #print(connected)
        else:
            connected = True
            print("Connected to the server")
    return client
        
        
def send(msg,client,ADDR):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    sending = True
    while sending :
        try:
            cl_ls[0].send(send_length)
            cl_ls[0].send(message)
            print(cl_ls[0].recv(2048).decode(FORMAT))
            sending = False
        except socket.error as error:
            cl_ls[0] = check_connection(ADDR)
            cl_ls[0].send(send_length)
            cl_ls[0].send(message)
            sending = False
            print(cl_ls[0].recv(2048).decode(FORMAT))
        
cl_ls = ["client"]
client = check_connection(ADDR)
cl_ls[0] = client
accept_more_barcodes = True
while accept_more_barcodes:
    input_value = input("Type 'exit' to close input box ")
    today = datetime.datetime.now()
    date_time = today.strftime("%m/%d/%Y, %H:%M:%S")
    input_value += ' /FBRC/ ' + date_time
    if (input_value).startswith("exit"):
        accept_more_barcodes = False
    else:  
        with open("fabric-barcodes.txt", "a") as f:
            f.write(input_value + "\n")
    send(input_value,cl_ls[0],ADDR)
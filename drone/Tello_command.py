#coding:utf-8
# Tello Python3 Control Demo 
#
# http://www.ryzerobotics.com/
#
# 1/1/2018

import threading 
import socket
import sys
import queue
import time

host = ''
port = 8889
locaddr = (host, port) 

send_q = queue.Queue()

def read_file(que):
    with open('command.txt', 'r') as f:
        for data in f:
            send_q.put(data.strip())

def recv_msg():
    recv_msg = socket1.recv(1024)
    if not recv_msg:
        sys.exit(0)
    recv_msg = recv_msg.decode()
    print(recv_msg)

def send_msg():
    msg = send_q.get()
    exec(msg)
    print(msg)
    if 'land' in msg:
        print('flag change')
        global flag
        flag = False

# Create a UDP socket
socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

socket1.bind(locaddr)

print("Waiting for connections")

# 起動
read_file(send_q)

class SendThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        global flag
        print("Starting " + self.name)
        while send_q.qsize() > 0:
            threadLock.acquire()
            if threadLock.state == True:
                print('wait thread1')
                threadLock.wait()
            send_msg()
            threadLock.state = True
            threadLock.notify()
            threadLock.release()
        print("Ending " + self.name)

class RecThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        global flag
        print("Starting " + self.name)
        while flag:
            threadLock.acquire()
            if threadLock.state == False:
                print('wait thread2')
                threadLock.wait(10)
            recv_msg()
            threadLock.state = False
            threadLock.notify()
            threadLock.release()
        print("Ending " + self.name)
        socket1.close()

flag = True
threadLock = threading.Condition()
threadLock.state = False
threads = []

print("please wait...")
time.sleep(3)

# Create new threads
thread1 = SendThread(1, "Send-Thread", 1)
thread2 = RecThread(2, "Receive-Thread", 2)

# Start new Threads
thread1.start()
thread2.start()

# Add threads to thread list
threads.append(thread1)
threads.append(thread2)

# Wait for all threads to complete
thread1.join()
flag = False
threadLock.acquire()
threadLock.notify()
threadLock.release()
thread2.join()

print("finish")
sys.exit()

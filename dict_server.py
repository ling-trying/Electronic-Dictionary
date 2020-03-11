'''
name: ling
date: 2020 - 3
email: lingling.ding00@gmail.com
modules:python 3.7.6
This is a dictionary checking,
this part is a simulated server
'''

from socket import *
import os
import time
import signal
import pymysql
import sys
from hashlib import sha1
import re
from time import sleep


# define global variable
dict_text = "./dict.txt"
HOST = '127.0.0.1'
PORT = 8888
ADDR = (HOST, PORT)


# main process
def main():
    # connect database
    db = pymysql.connect\
        ('localhost', 'root', password='', 'dict')

    # create socket
    s = socket()
    s. setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    # ignore the signal from child process
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        try:
            c, addr = s.accept()
            print("connect from", addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit('quit the server')
        except Exception as e:
            print(e)
            continue

        # create child process
        pid = os.fork()
        if pid == 0:
            s.close()
            # this is child process for receiving requests
            recv_request(c, db)
        else:
            # waiting for new connect
            c.close()
            continue  
    db.close()


# using to receiving requests
def recv_request(c, db):
    while True:
        msg = c.recv(1024).decode()
        l = msg.split(' ')
        if l[0] == 'R':
            register(c, db, l[1], l[2])
        elif l[0] == 'L':
            login(c, db, l[1], l[2])
        elif l[0] == 'Q':
            check_word(c, db, dict_text, l[1], l[2])
        elif l[0] == 'H':
            check_hist(c, db, l[1])
        else:
            sys.exit(0)  
    sys.exit(0)


# register a new account
def register(c, db, name, pswd):  
    cur = db.cursor()
    cur.execute("select name from user where name='%s';"%(name))
    data = cur.fetchone()
    if data != None:
        c.send('the name has been registered!'.encode())
        return
    # password encrypting
    s1 = sha1()
    s1.update(pswd.encode('utf8'))
    pwd2 = s1.hexdigest()
    # insert the user
    try:
        cur.execute("insert into user(name, passwd) \
            values ('%s', '%s')"%(name, pwd2))
        db.commit()
        c.send('Succeeded'.encode())
    except:
        db.rollback()
        c.send('Failed!'.encode())
    cur.close()


# login
def login(c, db, name, pswd):
    s1 = sha1()
    s1.update(pswd.encode('utf8'))
    pwd2 = s1.hexdigest()
    cur = db.cursor()
    slct = "select passwd from user where name='%s';"%(name)
    cur.execute(slct)
    rslt = cur.fetchall()
    if len(rslt) == 0:
        c.send('Can not find the user!'.encode())
    elif rslt[0][0] == pwd2:
        c.send('S'.encode())
    else:
        c.send('wrong password!'.encode())
    db.commit()
    cur.close()


# find explanation of word in dictionary
def check_word(c, db, file, word, name):
    # put the word in history
    cur = db.cursor()
    try:
        insert = f"insert into hist(name, word, time) \
            values ('{name}', '{word}', now());"
        cur.execute(insert)
        db.commit()
    except:
        db.rollback()
    # open the dictionary
    f = open(file, 'r')
    for line in f:
        if not line:
            return
        l = re.split(r'\s+', line)
        w = l[0]
        if w == word:
            interpret = ' '.join(l[1:])
            c.send(interpret.encode())
            return
    else:
        c.send("None".encode())       
    f.close()


# check the history
def check_hist(c, db, name):
    h = ''
    cur = db.cursor()
    select = f"select word, time from hist where name='{name}'"
    cur.execute(select)
    l = cur.fetchall()
    if l != None:
        for i in l[:-1]:
            h += f"|{i[0].center(20)}|{i[1].center(24)}|\n"
        for i in l[-1:]:
            h += f"|{i[0].center(20)}|{i[1].center(24)}|"
        c.send(h.encode())           
    else:
        c.send("Sorry,no history!".encode())


if __name__=="__main__":
    main()

'''
name: ling
date: 2020 - 3
email: lingling.ding00@gmail.com
modules:python 3.7.6
This is a dictionary checking,
this part is a simulated client
'''

from socket import *
import sys
import getpass


# create a connect
def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)
    # create a socket
    s = socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print(e)
        return
    # primary interface
    while True:
        print('''
            ------------Welcome-------------
            1.register    2.login     3.quit
            --------------------------------
            ''')
        try:
            cmd = input(' >> ')
            if cmd.strip() == '1':
                data, name = register(s)
            elif cmd.strip() == '2':
                data, name = login(s)
            elif cmd.strip() == '3':
                sys.exit(0)
            else:
                print('wrong input!')
                sys.stdin.flush() #clean input
                continue
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(e)
            continue
        # secondary interface
        if data == 'Succeeded':
            print('Login Success')
            after_login(s, name)
        else:
            print(data)
            continue


# register an account
def register(s):
    while True:
        name = input('your name: ')
        pswd = getpass.getpass()
        pswd1 = getpass.getpass('Again: ')
        if (' ' in name) or (' ' in pswd):
            print('Space is not allowed!')
            continue
        if pswd != pswd1:
            print('passwords are not same!')
            continue
        s.send(f"R {name} {pswd}".encode())
        data = s.recv(1024).decode()
        return data, name
            
        

# login the dict
def login(s):
    while True:
        name = input('your name: ')
        pswd = getpass.getpass()
        if (' ' in name) or (' ' in pswd):
            print('Space is not allowed!')
            continue
        s.send(f"L {name} {pswd}".encode())
        data = s.recv(1024).decode()
        return data, name


# after login, in the secondary interface
def after_login(s, name):
    while True:
        print('''
        ------------welcome--------------
        1.find word   2.history    3.quit
        ---------------------------------
        ''')
        try:
            cmd2 = input(' >> ') 
            if cmd2.strip() == '1':
                check_word(s, name)
            elif cmd2.strip() == '2':
                check_hist(s, name)
            elif cmd2.strip() == '3':
                return
            else:
                print('Wrong input!')
                continue
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(e)
            continue

# find the word in dictionary
def check_word(s, name):
    while True:
        word = input('word >> ')
        if word == "##":
            return
        if (not word) or (' ' in word):
            print('Wrong word, please check and input again!')
            continue
        s.send(f"Q {word} {name}".encode())
        data = s.recv(2048).decode()
        if data == 'None':
            print('Sorry, can not find the word!')
            return
        else:
            print(word, " : ",data)

# get the history
def check_hist(s, name):
    s.send(f"H {name}".encode())
    data = s.recv(4096).decode()
    print('+','-'*20,'+','-'*24,'+')
    print('|', 'word'.center(20), '|', 'time'.center(24), '|')
    print('+','-'*20,'+','-'*24,'+')
    print(data)
    print('+','-'*20,'+','-'*24,'+')


if __name__=="__main__":
    main()

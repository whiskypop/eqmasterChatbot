import sys  
import os  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'NGCBot_main')))  

from BotServer.MainServer import MainServer

if __name__ == '__main__':
    Ms = MainServer()
    Ms.processMsg()
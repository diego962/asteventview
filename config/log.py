from functools import wraps
import logging

class Log:
    
    def __init__(self):
        self.__log = logging.getLogger('eventview')
        self.__handler = logging.FileHandler("/home/diego/teste.log")
        self.__formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        self.__handler.setFormatter(self.__formatter)
        self.__log.addHandler(self.__handler)
        self.__log.setLevel(logging.INFO)

    def log(self, level=logging.INFO, msg=None):
        self.__log.log(level, msg)
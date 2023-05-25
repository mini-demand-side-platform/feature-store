from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def set_function(self):
        raise NotImplementedError


class Postgresql(Database):
    def set_function(self):
        pass


class Redis(Database):
    def set_function(self):
        pass

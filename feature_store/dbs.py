from abc import ABC, abstractmethod


class OnlineDatabase(ABC):
    @abstractmethod
    def set_function(self):
        pass

    @abstractmethod
    def get_feature(self):
        pass


class OfflineDatabase(ABC):
    @abstractmethod
    def set_function(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self):
        pass


class Postgresql(OfflineDatabase):
    def set_function(self):
        pass

    def write(self):
        pass

    def read(self):
        pass


class Redis(OnlineDatabase):
    def set_function(self):
        pass

    def get_feature(self):
        pass

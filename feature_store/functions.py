from abc import ABC, abstractmethod
from typing import Any, Dict

from .dbs import OfflineDatabase, OnlineDatabase


class FeatureStoreFunction(ABC):
    @abstractmethod
    def set_online_feature_function(self):
        pass

    @abstractmethod
    def set_offline_feature_function(self):
        pass

    @abstractmethod
    def get_online_feature(self):
        pass

    @abstractmethod
    def get_offline_feature(self):
        pass


class Mapping(FeatureStoreFunction):
    def set_online_feature_function(
        self, online_database: OnlineDatabase, rules: Dict[str, Any]
    ):
        pass

    def set_offline_feature_function(
        self, offline_database: OfflineDatabase, rules: Dict[str, Any]
    ):
        offline_database.create_function()

from __future__ import annotations

from abc import ABC, abstractmethod


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


class SimpleMapping(FeatureStoreFunction):
    def set_online_feature_function(self, Database):
        pass

    def set_offline_feature_function(self, Database):
        return super().offline_feature_function()

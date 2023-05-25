from __future__ import annotations

from abc import ABC, abstractmethod


class FeatureStoreFunction(ABC):
    @abstractmethod
    def online_feature_function(self):
        raise NotImplementedError

    @abstractmethod
    def offline_feature_function(self):
        raise NotImplementedError


class SimpleMapping(FeatureStoreFunction):
    def set_online_feature_function(self, Database):
        pass

    def set_offline_feature_function(self, Database):
        return super().offline_feature_function()

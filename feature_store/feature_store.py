from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Union

from .dbs import OfflineDatabase, OnlineDatabase
from .logger import get_logger

log = get_logger("feature_store")


class FeatureStoreFunctionType(Enum):
    STRING_MAPPING = 0
    SCALE = 1


feature_store_function_type_mapping = {
    "string_mapping": FeatureStoreFunctionType.STRING_MAPPING,
    "scale": FeatureStoreFunctionType.SCALE,
}


class FeatureStore:
    def get_online_feature(
        self,
        online_database: OnlineDatabase,
        feature_ids: List[str],
        feature_store_function_types: List[FeatureStoreFunctionType],
        inputs: List[Union[str, float, int]],
    ) -> List[Any]:
        assert len(feature_ids) == len(inputs)
        assert len(feature_ids) == len(feature_store_function_types)
        res = []
        for i in range(len(feature_ids)):
            if (
                feature_store_function_types[i]
                == FeatureStoreFunctionType.STRING_MAPPING
            ):
                key = (
                    feature_ids[i]
                    + "-"
                    + inputs[i]
                    + "-{}".format(FeatureStoreFunctionType.STRING_MAPPING.value)
                )
                if online_database.check_exist(key):
                    res.append(float(online_database.read(key)))
                else:
                    default_key = (
                        feature_ids[i]
                        + "-"
                        + "default"
                        + "-{}".format(FeatureStoreFunctionType.STRING_MAPPING.value)
                    )
                    if online_database.check_exist(default_key):
                        res.append(float(online_database.read(default_key)))
                    else:
                        res.append(None)
                        log.warning(
                            "No default key: {} for string_mapping".format(default_key)
                        )
            elif feature_store_function_types[i] == FeatureStoreFunctionType.SCALE:
                if not isinstance(inputs[i], str):
                    res.append(None)
                    log.warning(
                        "The input can not be str for the method string_mapping"
                    )
                    continue
                key = (
                    feature_ids[i]
                    + "-"
                    + inputs[i]
                    + "-{}".format(FeatureStoreFunctionType.SCALE.value)
                )
                if online_database.check_exist(key):
                    res.append(eval(online_database.read(key).format(inputs[i])))
                else:
                    res.append(None)
                    log.warning("Invalid key: {} for scale".format(key))
            else:
                res.append(None)
                log.warning(
                    "Invalid FeatureStoreFunctionType: {}".format(
                        feature_store_function_types[i]
                    )
                )
        return res

    def delete_online_feature(
        self, online_database: OnlineDatabase, feature_id: str
    ) -> None:
        delete_candidates = online_database.scan(feature_id)
        for delete_candidate in delete_candidates:
            online_database.delete(delete_candidate)

    def delete_offline_feature(
        self,
        offline_database: OfflineDatabase,
        feature_id: str,
    ) -> None:
        function_name = offline_database.read(
            table_name="feature",
            columns="function_name",
            condiction="WHERE feature_id = {}".format(feature_id),
        )["function_name"][0]
        offline_database.delete_function(function_name=function_name)
        offline_database.delete_row(
            table_name="feature", column_name="feature_id", target_value=feature_id
        )


class FeatureStoreFunction(ABC):
    @abstractmethod
    def set_online_feature_function(self):
        pass

    @abstractmethod
    def set_offline_feature_function(self):
        pass


class StringMapping(FeatureStoreFunction):
    def set_online_feature_function(
        self,
        online_database: OnlineDatabase,
        feature_id: str,
        mapping_rules: Dict[str, float],
    ) -> None:
        for k, v in mapping_rules.items():
            online_database.write(
                feature_id
                + "-"
                + k
                + "-{}".format(FeatureStoreFunctionType.STRING_MAPPING.value),
                str(v),
            )

    def set_offline_feature_function(
        self,
        offline_database: OfflineDatabase,
        function_name: str,
        mapping_rules: Dict[str, float],
    ) -> None:
        offline_database.create_string_mapping_function(
            function_name=function_name, mapping_rules=mapping_rules
        )


class Scale(FeatureStoreFunction):
    def set_online_feature_function(
        self,
        online_database: OnlineDatabase,
        feature_id: str,
        math_operation: str,
    ) -> None:
        online_database.write(
            feature_id + "-{}".format(FeatureStoreFunctionType.SCALE.value),
            math_operation,
        )

    def set_offline_feature_function(
        self,
        offline_database: OfflineDatabase,
        function_name: str,
        math_operation: str,
    ) -> None:
        offline_database.create_scale_function(
            function_name=function_name, math_operation=math_operation.format("x")
        )

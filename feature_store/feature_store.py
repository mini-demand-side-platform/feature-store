from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Union

from .dbs import DatabaseValueType, OfflineDatabase, OnlineDatabase
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
        feature_store_function_types: List[str],
        inputs: List[Union[str, float, int]],
    ) -> List[Any]:
        assert len(feature_ids) == len(inputs)
        assert len(feature_ids) == len(feature_store_function_types)
        res = []
        for i in range(len(feature_ids)):
            if (
                feature_store_function_type_mapping[feature_store_function_types[i]]
                == FeatureStoreFunctionType.STRING_MAPPING
            ):
                if not isinstance(inputs[i], str):
                    res.append(None)
                    log.warning(
                        "The input can only be str for the method string_mapping"
                    )
                    continue
                key = (
                    feature_ids[i]
                    + "-"
                    + inputs[i]
                    + "-{postfix}".format(
                        postfix=FeatureStoreFunctionType.STRING_MAPPING.value
                    )
                )
                if online_database.check_exist(key):
                    res.append(float(online_database.read(key)))
                else:
                    default_key = (
                        feature_ids[i]
                        + "-"
                        + "default"
                        + "-{postfix}".format(
                            postfix=FeatureStoreFunctionType.STRING_MAPPING.value
                        )
                    )
                    if online_database.check_exist(default_key):
                        res.append(float(online_database.read(default_key)))
                    else:
                        res.append(None)
                        log.warning(
                            "No default key: {default_key} for string_mapping".format(
                                default_key=default_key
                            )
                        )
            elif (
                feature_store_function_type_mapping[feature_store_function_types[i]]
                == FeatureStoreFunctionType.SCALE
            ):
                if isinstance(inputs[i], str):
                    res.append(None)
                    log.warning("The input can not be str for the method scale")
                    continue
                key = feature_ids[i] + "-{postfix}".format(
                    postfix=FeatureStoreFunctionType.SCALE.value
                )
                if online_database.check_exist(key):
                    res.append(eval(online_database.read(key).format(inputs[i])))
                else:
                    res.append(None)
                    log.warning("Invalid key: {key} for scale".format(key=key))
            else:
                res.append(None)
                log.warning(
                    "Invalid FeatureStoreFunctionType: {function_type}".format(
                        function_type=feature_store_function_types[i]
                    )
                )
        return res

    def delete_online_feature(
        self, online_database: OnlineDatabase, feature_id: str
    ) -> None:
        delete_candidates = online_database.scan(feature_id)[0]
        for delete_candidate in delete_candidates:
            online_database.delete(delete_candidate)

    def delete_offline_feature(
        self,
        offline_database: OfflineDatabase,
        feature_id: str,
    ) -> None:
        function_name = offline_database.read(
            table_name="feature",
            column_names=["function_name"],
            condiction="WHERE feature_id = '{feature_id}'".format(
                feature_id=feature_id
            ),
        )["function_name"][0]
        offline_database.delete_function(function_name=function_name)
        offline_database.delete_row(
            table_name="feature", column_name="feature_id", target_value=feature_id
        )

    def generate_offline_table(
        self, offline_database: OfflineDatabase, feature_store_id: str
    ):
        offline_table_name = offline_database.read(
            table_name="feature_store",
            column_names=["offline_table_name"],
            condiction="WHERE feature_store_id = {feature_store_id}".format(
                feature_store_id=feature_store_id
            ),
        )["offline_table_name"][0]
        feature_info = offline_database.read(
            table_name="feature",
            column_names=[
                "feature_name",
                "function_name",
                "source_table_name",
                "source_column_name",
            ],
            condiction="where feature_store_id = {feature_store_id}".format(
                feature_store_id=feature_store_id
            ),
        )
        if len(set(feature_info["source_table_name"])) > 1:
            raise ValueError(
                (
                    "Only support source table from same place "
                    "but having {source_table_names}"
                ).format(
                    source_table_names=",".join(
                        list(set(feature_info["source_table_name"]))
                    )
                )
            )
        offline_database.delete_table(table_name=offline_table_name)
        offline_database.create_table(
            table_name=offline_table_name,
            column_names=feature_info["feature_name"],
            column_types=[DatabaseValueType.FLOAT] * len(feature_info["feature_names"]),
        )
        apply_function_column_names = []
        for function_name, column_name in zip(
            feature_info["function_name"], feature_info["source_column_name"]
        ):
            apply_function_column_names.append(
                "{function_name}({column_name})".format(
                    function_name=function_name, column_name=column_name
                )
            )
        offline_database.write_from_table(
            target_table_name=offline_table_name,
            target_column_names=feature_info["feature_name"],
            source_table_name=feature_info["source_table_name"][0],
            source_column_names=apply_function_column_names,
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
                + "-{postfix}".format(
                    postfix=FeatureStoreFunctionType.STRING_MAPPING.value
                ),
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
            feature_id
            + "-{postfix}".format(postfix=FeatureStoreFunctionType.SCALE.value),
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

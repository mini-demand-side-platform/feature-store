from typing import List

from pydantic import BaseModel


class ListFeatureStoreOutput(BaseModel):
    feature_store_id: List[str]
    feature_store_name: List[str]


class GetFeatureStoreOutput(BaseModel):
    feature_store_id: List[str]
    feature_store_name: List[str]
    description: List[str]
    offline_table_id: List[str]

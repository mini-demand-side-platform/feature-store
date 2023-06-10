import os
from dataclasses import dataclass

feature_mapping = {
    0: {"layout_style": "AB"},
    1: {"layout_style": "RU"},
    2: {"layout_style": "GY"},
    3: {"layout_style": "MR"},
    4: {"layout_style": "BK"},
    5: {"layout_style": "BX"},
    6: {"layout_style": "RZ"},
    7: {"layout_style": "TY"},
    8: {"category": "Shirt"},
    9: {"layout_style": "DX"},
}


@dataclass
class DBServerInfo:
    host: str
    port: str
    database: str
    username: str
    password: str


oltp_server_info = DBServerInfo(
    host=os.getenv("oltp_host", "localhost"),
    port=os.getenv("oltp_port", "5432"),
    database=os.getenv("oltp_database", "oltp"),
    username=os.getenv("oltp_username", "dsp"),
    password=os.getenv("oltp_password", "dsppassword"),
)
olap_server_info = DBServerInfo(
    host=os.getenv("olap_host", "localhost"),
    port=os.getenv("olap_port", "5432"),
    database=os.getenv("olap_database", "olap"),
    username=os.getenv("olap_username", "dsp"),
    password=os.getenv("postgres_password", "dsppassword"),
)
feature_store_server_info = DBServerInfo(
    host=os.getenv("feature_store_host", "localhost"),
    port=os.getenv("feature_store_port", "5432"),
    database=os.getenv("feature_store_database", "feature_store"),
    username=os.getenv("feature_store_username", "dsp"),
    password=os.getenv("feature_store_password", "dsppassword"),
)
cache_server_info = DBServerInfo(
    host=os.getenv("cache_host", "localhost"),
    port=os.getenv("cache_port", "6379"),
    database=os.getenv("cache_database", "cache"),
    username=os.getenv("cache_username", "dsp"),
    password=os.getenv("cache_password", "dsppassword"),
)

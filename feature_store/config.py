import os
from dataclasses import dataclass


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

cache_server_info = DBServerInfo(
    host=os.getenv("cache_host", "localhost"),
    port=os.getenv("cache_port", "6379"),
    database=os.getenv("cache_database", "cache"),
    username=os.getenv("cache_username", "dsp"),
    password=os.getenv("cache_password", "dsppassword"),
)

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

import psycopg2
import redis

from .config import DBServerInfo


class DatabaseValueType(Enum):
    BOOL = 1
    INTEGER = 2
    FLOAT = 3
    STR = 4


class OnlineDatabase(ABC):
    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def check_exist(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def scan(self):
        pass


class OfflineDatabase(ABC):
    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def delete_table(self):
        pass

    @abstractmethod
    def delete_row(self):
        pass

    @abstractmethod
    def create_string_mapping_function(self):
        pass

    @abstractmethod
    def delete_function(self):
        pass


class Postgresql(OfflineDatabase):
    def __init__(self, db_server_info: DBServerInfo) -> None:
        self.conn = psycopg2.connect(
            host=db_server_info.host,
            port=db_server_info.port,
            database=db_server_info.database,
            user=db_server_info.username,
            password=db_server_info.password,
        )
        self.database_value_type_mapping = {
            DatabaseValueType.BOOL: "boolean",
            DatabaseValueType.INTEGER: "integer",
            DatabaseValueType.FLOAT: "double precision",
            DatabaseValueType.STR: "TEXT",
        }

    def create_table(self, table_name: str) -> None:
        cur = self.conn.cursor()

        cur.execute(
            """
            CREATE TABLE {} (
                row_id SERIAL PRIMARY KEY,
            );
            """.format(
                table_name
            )
        )
        cur.close()

    def write(
        self,
        table_name: str,
        data: Dict[str, List[Any]],
        returning_columns: Optional[List[str]] = None,
    ) -> Optional[Dict[str, List[str]]]:
        res = None
        cur = self.conn.cursor()
        formated_data = []
        ks = list(data.keys())
        data_len = -1
        for k in ks:
            if data_len == -1:
                data_len = len(data[k])
            else:
                if data_len != len(data[k]):
                    raise "Data length different"
        for i in range(data_len):
            row = []
            for k in ks:
                row.append(data[k][i])
            formated_data.append(tuple(row))
        insert_query = """
            INSERT INTO {} ({})
            VALUES ({})
            """.format(
            table_name,
            ",".join(ks),
            ",".join(
                ["%s"] * len(ks),
            ),
        )
        if returning_columns is not None:
            res = {}
            for returning_column in returning_columns:
                res[returning_column] = []
            insert_query += " RETURNING {};".format(",".join(returning_columns))

            returning = cur.fetchall()
            for row in returning:
                for i in range(len(returning_columns)):
                    res[returning_columns[i]].append(row[i])
        else:
            insert_query += ";"
            cur.execute(insert_query, formated_data)

        # Commit the changes to the database
        self.conn.commit()
        cur.close()
        return res

    def read(
        self, table_name: str, columns: List[str], condiction: Optional[str] = None
    ) -> Dict[str, List[Any]]:
        cur = self.conn.cursor()
        if condiction is None:
            cur.execute("SELECT {} FROM {};".format(columns.join(","), table_name))
        else:
            cur.execute(
                "SELECT {} FROM {} {};".format(
                    ",".join(columns), table_name, condiction
                )
            )
        res = {}
        rows = cur.fetchall()
        for row in rows:
            for i in range(len(row)):
                if columns[i] not in res:
                    res[columns[i]] = []
                res[columns[i]].append(row[i])
        cur.close()
        return res

    def delete_table(self, table_name: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            DROP TABLE IF EXISTS {};
            """.format(
                table_name
            )
        )

        # Commit the changes to the database
        self.conn.commit()
        cur.close()

    def delete_row(self, table_name: str, column_name: str, target_value: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            DELETE FROM {} WHERE {}={};
            """.format(
                table_name, column_name, target_value
            )
        )
        self.conn.commit()
        cur.close()

    def create_string_mapping_function(
        self,
        function_name: str,
        mapping_rules: Dict[str, float],
    ) -> None:
        cur = self.conn.cursor()
        mapping_function = ""
        for k, v in mapping_rules.items():
            if k != "default":
                if len(mapping_function) == 0:
                    mapping_function += "IF x={} THEN \n\tresult := {} \n".format(k, v)
                else:
                    mapping_function += "ELSIF x={} THEN \n\tresult := {} \n".format(
                        k, v
                    )
        mapping_function += "ELSE\n\tresult := {}\nEND IF;\nRETURN result;".format(
            mapping_rules["default"]
        )
        function_query = """
            CREATE FUNCTION {}(x {})
            RETURNS {} AS $$
            DECLARE
                result {};
            BEGIN
            {}
            END;
            $$ LANGUAGE plpgsql;
            """.format(
            function_name,
            self.database_value_type_mapping[DatabaseValueType.STR],
            self.database_value_type_mapping[DatabaseValueType.FLOAT],
            self.database_value_type_mapping[DatabaseValueType.FLOAT],
            mapping_function,
        )

        cur.execute(function_query)
        self.conn.commit()
        cur.close()

    def create_scale_function(
        self,
        function_name: str,
        math_operation: str,
    ) -> None:
        cur = self.conn.cursor()

        function_query = """
            CREATE FUNCTION {}(x {})
            RETURNS {} AS $$
            DECLARE
                result {};
            BEGIN
                result := {}
                RETURN result;
            END;
            $$ LANGUAGE plpgsql;
            """.format(
            function_name,
            self.database_value_type_mapping[DatabaseValueType.FLOAT],
            self.database_value_type_mapping[DatabaseValueType.FLOAT],
            self.database_value_type_mapping[DatabaseValueType.FLOAT],
            math_operation,
        )

        cur.execute(function_query)
        self.conn.commit()
        cur.close()

    def delete_function(self, function_name: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            DELETE FUNCTION IF EXISTS {};
            """.format(
                function_name
            )
        )
        self.conn.commit()
        cur.close()


class Redis(OnlineDatabase):
    def __init__(self, db_server_info: DBServerInfo) -> None:
        self.conn = redis.Redis(
            host=db_server_info.host,
            port=db_server_info.port,
        )

    def read(
        self,
        key: str,
    ) -> str:
        return self.conn.get(key).decode()

    def check_exist(self, key) -> bool:
        return self.conn.exists(key)

    def write(self, key: str, value: str) -> None:
        self.conn.set(key, value)

    def delete(self, key) -> None:
        self.conn.delete(key)

    def scan(self, pattern) -> List[str]:
        keys = []
        cursor = "0"
        while cursor != 0:
            cursor, matched_key = self.conn.scan(cursor=cursor, match=pattern)
            keys.append(matched_key)
        return keys

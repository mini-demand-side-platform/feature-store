from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

import psycopg2

from .config import DBServerInfo


class DatabaseValueType(Enum):
    BOOL = 1
    INTEGER = 2
    FLOAT = 3
    STR = 4


class OnlineDatabase(ABC):
    @abstractmethod
    def get_online_feature(self):
        pass

    @abstractmethod
    def create_function(self):
        pass

    @abstractmethod
    def delete_function(self):
        pass


class OfflineDatabase(ABC):
    @abstractmethod
    def create_offline_table(self):
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
    def create_function(self):
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

    def create_offline_table(self, table_name: str) -> None:
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

    def write(self, table_name: str, data: Dict[str, List[Any]]) -> None:
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
            VALUES ({});
            """.format(
            table_name, ",".join(ks), ",".join(["%s"] * len(ks))
        )

        cur.execute(insert_query, formated_data)
        # Commit the changes to the database
        self.conn.commit()
        cur.close()

    def read(
        self, table: str, columns: List[str], condiction: Optional[str] = None
    ) -> Dict[str, Any]:
        cur = self.conn.cursor()
        if condiction is None:
            cur.execute("SELECT {} FROM {};".format(columns.join(","), table))
        else:
            cur.execute(
                "SELECT {} FROM {} {};".format(",".join(columns), table, condiction)
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

        # Commit the changes to the database
        self.conn.commit()
        cur.close()

    def create_mapping_function(
        self,
        function_name: str,
        input_value_type: DatabaseValueType,
        output_value_type: DatabaseValueType,
        mapping_rules: Dict["str", Any],
    ) -> None:
        cur = self.conn.cursor()
        function_query = ""
        for k, v in mapping_rules.items():
            if k != "default":
                if len(function_query) == 0:
                    function_query += "IF {} THEN \n\tresult := {} \n".format(k, v)
                else:
                    function_query += "ELSIF {} THEN \n\tresult := {} \n".format(k, v)
        function_query += "ELSE\n\tresult := {}\nEND IF;".format(
            mapping_rules["default"]
        )
        cur.execute(
            """
            CREATE FUNCTION {}(input {})
            RETURNS {} AS $$
            DECLARE
                result {};
            BEGIN
                IF input > 0 THEN
                    result := 'Positive';
                ELSE
                    result := 'Negative';
                END IF;

                -- Return the result
                RETURN result;
            END;
            $$ LANGUAGE plpgsql;
            """.format(
                function_name,
                self.database_value_type_mapping[input_value_type],
                self.database_value_type_mapping[output_value_type],
                self.database_value_type_mapping[output_value_type],
            )
        )


class Redis(OnlineDatabase):
    def __init__(self, db_server_info: DBServerInfo) -> None:
        pass

    def set_function(self):
        pass

    def get_feature(self):
        pass

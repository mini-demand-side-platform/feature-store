from unittest.mock import MagicMock, patch

from feature_store.data_templates import DBServerInfo
from feature_store.dbs import Postgresql

test_server_info = DBServerInfo(
    host="localhost",
    port="5432",
    database="olap",
    username="dsp",
    password="dsppassword",
)


class TestPostgresql:
    def test_read(self):
        # Create a MagicMock object to mock cur.fetchall()
        mock_fetchall = MagicMock()

        # Set the desired return value for the mocked fetchall()
        mock_fetchall.return_value = [(1997, False), (1792, False), (1072, True)]

        # Create a MagicMock object to mock cur
        mock_cur = MagicMock()

        # Attach the mocked fetchall() to cur
        mock_cur.fetchall = mock_fetchall

        # Create a MagicMock object to mock psycopg2.connect()
        mock_connect = MagicMock()

        # Attach the mocked cur to the connection
        mock_connect.cursor.return_value = mock_cur

        with patch("psycopg2.connect", return_value=mock_connect):
            pg = Postgresql(test_server_info)

            t = pg.read(
                table_name="ctr", column_names=["ad_id", "status"], condiction="LIMIT 3"
            )
        assert len(t.keys()) == 2

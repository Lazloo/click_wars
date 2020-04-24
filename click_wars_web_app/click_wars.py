import sqlalchemy
from loguru import logger
from time import time
import MySQLdb
import sshtunnel
import get_pw
import pandas as pd


class ClickWars:
    def __init__(self):
        self.logger = logger
        self.logger.add(sink='log.log')
        self.local_use = True
        self.db_host = 'lazloo.mysql.pythonanywhere-services.com'
        self.host_local = '127.0.0.1'
        self.port_db = 3306
        self.user, self.pw, self.pw_db = get_pw.get_pw()
        sshtunnel.SSH_TIMEOUT = 5.0
        sshtunnel.TUNNEL_TIMEOUT = 5.0
        pass

    def create_ssh_connection(self):
        tunnel = sshtunnel.SSHTunnelForwarder(
            'ssh.pythonanywhere.com',
            ssh_username=self.user, ssh_password=self.pw,
            remote_bind_address=(self.db_host, self.port_db)
        )
        return tunnel

    def create_mysql_connection(self, host, port, db: str = 'lazloo$click_wars'):
        connection = MySQLdb.connect(
            user=self.user, password=self.pw_db,
            host=host, port=port,
            database=db)

        return connection

    def create_sqlalchemy_connection(self, host, port, db: str = 'lazloo$click_wars'):
        conn_address = 'mysql://' + self.user + ':' + self.pw_db + '@' + host + ':' + str(port) + '/' + db
        engine = sqlalchemy.create_engine(conn_address, pool_recycle=280)

        return engine

    def return_dataframe(self, sql: str):
        if self.local_use:
            tunnel = self.create_ssh_connection()
            tunnel.start()
            con = self.create_mysql_connection(host=self.host_local, port=tunnel.local_bind_port)
            df = pd.read_sql(sql=sql, con=con)
            con.close()
            tunnel.close()
        else:
            con = self.create_mysql_connection(host=self.db_host, port=self.port_db)
            df = pd.read_sql(sql=sql, con=con)
            con.close()
        return df

    def commit_sql_query(self, sql: str):
        if self.local_use:
            with self.create_ssh_connection() as tunnel:
                con = self.create_mysql_connection(host=self.host_local, port=tunnel.local_bind_port)
                my_cursor = con.cursor()
                my_cursor.execute(sql)

                con.commit()
                my_cursor.close()
                con.close()
        else:
            con = self.create_mysql_connection(host=self.db_host, port=self.port_db)
            my_cursor = con.cursor()
            my_cursor.execute(sql)
            con.commit()
            my_cursor.close()
            con.close()

    def update_click(self, session_id: int, player_id):
        sql_update = """
        UPDATE lazloo$click_wars.click_distribution
        SET 
            count_clicks = count_clicks + 1
        where session_id = /*session_id*/ and player_id = /*player_id*/
        ;
        """.replace('/*session_id*/', str(session_id)).replace('/*player_id*/', str(player_id))
        self.commit_sql_query(sql=sql_update)

    def reset_clicks(self, session_id: int):
        sql_update = """
        UPDATE lazloo$click_wars.click_distribution
        SET 
            count_clicks = 1
        where session_id = /*session_id*/ 
        ;
        """.replace('/*session_id*/', str(session_id))
        self.commit_sql_query(sql=sql_update)

    def get_clicks(self, session_id):

        sql = """
            select * 
            from lazloo$click_wars.click_distribution
            where session_id = /*session_id*/
        """.replace('/*session_id*/', str(session_id))
        df = self.return_dataframe(sql=sql)
        return df

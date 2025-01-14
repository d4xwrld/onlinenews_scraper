from pymongo import MongoClient
from dotenv import load_dotenv
import os
import ast
load_dotenv()
class DBMongo:
    def __init__(self, HOST, USERNAME, PASSWORD, AUTH_SOURCE):
        self.DB_CLIENT = None
        self.USERNAME = USERNAME
        self.PASSWORD = PASSWORD
        self.AUTH_SOURCE = AUTH_SOURCE
        self.HOST = HOST.partition(':')[0]
        self.PORTS = ast.literal_eval(os.getenv('DB_PORTS', "[]"))

    def ConnectDatabase(self):
        ConfigDBDict = dict(
            username=self.USERNAME,
            password=self.PASSWORD,
            authSource=self.AUTH_SOURCE,
            authMechanism='SCRAM-SHA-1',
            directConnection=True
        )
        for port in self.PORTS:
            try:
                ClientDatabase = MongoClient(f"{self.HOST}:{port}", **ConfigDBDict)
                server_info = ClientDatabase.admin.command("ismaster")
                is_secondary = server_info.get("secondary", False)
                if not is_secondary:
                    self.DB_CLIENT = ClientDatabase
                    print(f"Connected to primary at {self.HOST}:{port}")
                    return self.DB_CLIENT

                print(f"Connected to {self.HOST}:{port} but it's a secondary. Trying next port...")
            
            except Exception as e:
                print(f"Connection failed for {self.HOST}:{port} - {e}")
        
    def DisconnectDatabase(self):
        if self.DB_CLIENT is not None:
            return self.DB_CLIENT.close()
        
    def GetDatabase(self, db_name=None):
        if self.DB_CLIENT is None:
            self.ConnectDatabase()
        if db_name is None:
            return self.DB_CLIENT.admin
        else:
            return self.DB_CLIENT[db_name]

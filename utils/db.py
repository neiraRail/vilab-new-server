import pymongo
from os import environ as env

BUFFER_SIZE = 1000
mongohost = env.get("MONGO_HOST", "localhost")

class Saver:
    def __init__(self):
        self.buffer = []
        myclient = pymongo.MongoClient(f"mongodb://{mongohost}:27017/")
        # Probar conexión
        try:
            myclient.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            print("MongoDB no disponible")
            raise Exception("MongoDB no disponible")
        self.mydb = myclient["inercial"]
        self._isNodeSet = False
    

    def save(self, data):
        if not self.validate(data):
            raise Exception("Invalid data")
        
        if not self._isNodeSet:
            self._isNodeSet = True
            node = data['nd']
            self.db = self.mydb[f"lecturas{node}"]
        
        self.buffer.append(data)

        if len(self.buffer) >= BUFFER_SIZE:
            try:
                self.db.insert_many(self.buffer)
            except:
                print("Error saving data")
            else:
                self.buffer = []
        return True

    def validate(self, data):
        if not isinstance(data, dict):
            return False
        if 'ax' not in data or 'ay' not in data or 'az' not in data or 'gx' not in data or 'gy' not in data or 'gz' not in data or 'mx' not in data or 'my' not in data or 'mz' not in data or 'tp' not in data or 'st' not in data or 'nd' not in data or 'tm' not in data or 'dt' not in data:
            return False
        return True
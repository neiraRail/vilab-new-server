import pymongo
from os import environ as env

class InitException(Exception):
    pass

class SaveException(Exception):
    pass


BUFFER_SIZE = 100
mongohost = env.get("MONGO_HOST", "localhost")

class Saver:
    def __init__(self):
        try:
            self.buffer = []
            myclient = pymongo.MongoClient(f"mongodb://{mongohost}:27017/", serverSelectionTimeoutMS=2000)
            # Probar conexión
            myclient.server_info()

            self.mydb = myclient["inercial"]
            self._isNodeSet = False
        except pymongo.errors.ServerSelectionTimeoutError:
            raise InitException("MongoDB no disponible")
        except BaseException as e:
            raise InitException(f"Error al iniciar el objeto Saver: {e}")
    

    def save(self, data):
        # if not self.validate(data):
        #     raise Exception("Invalid data")
        try:
            if not self._isNodeSet:
                self._isNodeSet = True
                node = data['nd']
                self.db = self.mydb[f"lecturas{node}"]
            
            # print(data["tm"])
            # self.buffer.append(data) # por alguna razon tienen que estar en orden alrevez
            self.buffer.insert(0, data)

            if len(self.buffer) >= BUFFER_SIZE:
                self.db.insert_many(self.buffer)
                self.buffer = []
                
            return True
        except BaseException as e:
            raise SaveException(f"Error al guardar los datos: {e}")
        
    def send_buffer(self):
        # Send whats left in the buffer if there is any
        try:
            if len(self.buffer) > 0:
                self.db.insert_many(self.buffer)
                self.buffer = []
        except BaseException as e:
            raise SaveException(f"Error al guardar los datos restantes: {e}")


    def validate(self, data):
        if not isinstance(data, dict):
            return False
        if 'ax' not in data or 'ay' not in data or 'az' not in data or 'gx' not in data or 'gy' not in data or 'gz' not in data or 'mx' not in data or 'my' not in data or 'mz' not in data or 'tp' not in data or 'st' not in data or 'nd' not in data or 'tm' not in data or 'dt' not in data:
            return False
        return True
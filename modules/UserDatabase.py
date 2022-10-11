from modules.croqShared import database_path
import os, json

def getPath(user):
    return os.path.join(database_path, user)+".db"

def load(user):
    try:
        return json.loads(open(getPath(user), "r").read())
    except Exception as e:
        print(f"The error '{e}' occurred")
        return []
        
def save(user, data):
    return open(getPath(user), "w").write(json.dumps(data))

def _get_user_from_file(file):
    if not os.path.isfile(os.path.join(database_path, file)):
        return None
    ret = file.rsplit( ".", 1 )
    if len(ret) != 2:
        return None
    return ret[0]

def listUsers():
    users = [_get_user_from_file(f) for f in os.listdir(database_path)]
    return [user for user in users if user]
from modules import shared
import os, json

def getPath(user):
    return os.path.join(shared.cmd_opts.database_path, user)+".db"

def load(user):
    try:
        return json.loads(open(getPath(user), "r").read())
    except Exception as e:
        print(f"The error '{e}' occurred")
        return []
        
def save(user, data):
    return open(getPath(user), "w").write(json.dumps(data))
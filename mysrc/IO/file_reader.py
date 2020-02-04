import json

def myhost(configpath):
    import sqlalchemy
    url = ''
    try:
        with open(configpath) as json_file:
            data = json.load(json_file)["DB"]
            url = sqlalchemy.engine.url.URL(
                drivername=data["drivername"],
                username=data["username"],
                password=data["password"],
                database=data["database"],
                port=data["port"]
            )
            print(f"connecting with {url}")
        return url
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        return 'file error'
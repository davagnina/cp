import sys, mariadb


# retrieve data from json and open connection to db
def db_connector():
    try:
        conn = mariadb.connect(
            user="cryptodb",
            password="D0dO$3uW.kxw533q",
            host="10.1.5.18",
            port=3307,
            database="cryptodb",
            autocommit=True)
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return conn
       
import pyodbc

def connect():
    server = '.'
    database = 'Restaurant_Recommendation'
    username = 'RaphaelArnold'
    password = 'P8N3kj754%'
    print("connecting...")
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';TRUSTED_CONNECTION=yes')
    print("connected")
    return connection
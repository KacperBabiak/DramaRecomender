import getpass
import mysql.connector
import pandas as pd
from mysql.connector import errorcode
from sqlalchemy import create_engine
import pymysql


#pw = getpass.getpass("Enter password: ")



host = 'sql7.freemysqlhosting.net'
port = '3306'
database = 'sql7604015'

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                       .format(user=user,
                               pw=password,
                               host = host,
                               db=database))

lis = ['dupa', 'dupsko','duperka']
df = pd.DataFrame(lis, columns= ['dup'])
print(df)

df.to_sql('dupa', con = engine, if_exists = 'replace', chunksize = 1000)


    

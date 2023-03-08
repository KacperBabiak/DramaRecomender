import scrapper
import recommender
import pandas as pd
import time

st = time.time()
try:
    rec = recommender.recommender()
    rec.insert_data_to_sql()
except Exception as e: 
    print(e)
    print("cos nie pykło")
finally:
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
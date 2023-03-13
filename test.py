import scrapper
import recommender
import pandas as pd
import time

st = time.time()

rec = recommender.recommender()
rec.get_recommendations_for_user('10105451')
try:
    print('dupa')
    
    #rec.insert_data('sql7604015','cuCZhBqBCY')
except Exception as e: 
    print(e)
    print("cos nie pykło")
finally:
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
import scrapper
import recommender
import pandas as pd
import time

#scr= scrapper.Scrapper()
#df = scr.get_all_shows_data()
#df.to_csv('all_shows_data.csv')
#df = pd.read_csv('all_shows_data.csv')
#print(df)

#st = time.time()

rec = recommender.Recommender()
#print(rec.get_recommendations('Goblin',10))
df = rec.get_recommendations_for_user('MellOut',150)
'''
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
'''
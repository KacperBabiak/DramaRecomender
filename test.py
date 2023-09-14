import scrapper
import recommender
import pandas as pd
import time
import recommender_colab

#scr= scrapper.Scrapper()
#df = scr.get_all_shows_data()
#df.to_csv('all_shows_data.csv')
#df = pd.read_csv('all_shows_data.csv')
#print(df)

#print(rec.get_recommendations('Goblin',10))
#df = rec.get_recommendations_for_user('MellOut',150)

st = time.time()


try:
    print('dupa')
    rec = recommender_colab.Recommmender_Colab()
    rec.model_fit()
   
except Exception as e: 
    print(e)
    print("cos nie pykło")
finally:
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')

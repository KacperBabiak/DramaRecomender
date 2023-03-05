import scrapper
import recommender
import pandas as pd
import time

st = time.time()
rec = recommender.recommender()
rec.get_recommendations('The Untamed')

et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
import scrapper
import getpass
import mysql.connector
import pandas as pd
from mysql.connector import errorcode
from sqlalchemy import create_engine
import pymysql

class recommender:

    def __init__(self):
        self.scr = scrapper.scrapper()
        self.get_data()
        #print(self.data)
        self.recommend_prepare()
        pass

    def get_data(self):
        self.data = pd.read_csv('shows_data.csv')

    def data_to_csv(self):
        
        self.data = self.scr.get_all_shows_data()
        self.data.to_csv('shows_data.csv',index=False)

    def insert_data_to_sql(self,user,password):
        host = 'sql7.freemysqlhosting.net'
        database = 'sql7604015'

        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                       .format(user=user,
                               pw=password,
                               host = host,
                               db=database))
        print('connected')
        self.data.to_sql('Shows data', con = engine, if_exists = 'replace', chunksize = 1000)
        

        print('end')
                
    

    def clean_data(self, x ):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        else:
            if isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            else:
                return ''

    def recommend_prepare(self):
    
        # Apply clean_data function to your features.
        features = ['Screenwriter', 'Director']

        for feature in features:
            self.data[feature] = self.data[feature].apply(self.clean_data)
        
        
        #Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
        #tfidf = TfidfVectorizer(stop_words='english')
        
        
        #Construct the required TF-IDF matrix by fitting and transforming the data
        self.data = self.data.fillna('')
        df_all = self.data['Director']  + self.data['Tag'] +self.data['Description'] + self.data['Genres']  + self.data['Country']  + self.data['Screenwriter']
        
        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(df_all)
        #tfidf_matrix = tfidf.fit_transform(df_all)
        
        # Compute the cosine similarity matrix
        #self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        self.cosine_sim = cosine_similarity(count_matrix, count_matrix)
        
        #Construct a reverse map of indices and movie titles
        
        self.indices = pd.Series(self.data.index, index=self.data['Name']).drop_duplicates()
        


    # Function that takes in movie title as input and outputs most similar movies
    def get_recommendations(self,title):
        # Get the index of the movie that matches the title
        idx = self.indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(self.cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:101]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        
        #print(self.data['Name'].iloc[movie_indices])
        return self.data['Name'].iloc[movie_indices]
    

    def get_recommendations_on_list(self,df):
        
        scores_dic = {}

        for index,row in df.iterrows():
            recomm = self.get_recommendations(row['Title'])

            for show in recomm:
                if show in scores_dic:
                    
                    #print(row['Rating'])
                    scores_dic[show]=scores_dic[show]+row['Rating']
                else:
                    scores_dic[show]=row['Rating']

        sorted_dic = dict(sorted(scores_dic.items(), key=lambda item: item[1], reverse= True))
        print(sorted_dic)

    def get_recommendations_for_user(self,user):
        user_list = self.scr.get_user_list(user)

        return self.get_recommendations_on_list(user_list)




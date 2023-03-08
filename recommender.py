from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
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
        #self.get_data()
        #self.recommend_prepare()
        pass

    def insert_data_to_sql(self,user,password):
        scr = scrapper.scrapper()
        self.data = scr.get_all_shows_data()

        host = 'sql7.freemysqlhosting.net'
        database = 'sql7604015'

        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                       .format(user=user,
                               pw=password,
                               host = host,
                               db=database))

        self.data.to_sql('Shows data', con = engine, if_exists = 'replace', chunksize = 1000)
                

    # Function that computes the weighted rating of each movie
    def weighted_rating(self, df, m, C):
        v = df['Score']
        R = df['Number_of_rates']
        # Calculation based on the IMDB formula
        return (v/(v+m) * R) + (m/(m+v) * C)


    def recommend_prepare(self):
        # Calculate mean of vote average column
        C = self.data['Score'].mean()
        print(C)

        # Calculate the minimum number of votes required to be in the chart, m
        m = self.data['Number_of_rates'].quantile(0.65)
        print(m)

        #czy wprowadzic filtracje tych z małą ilością głosów?

        # Define a new feature 'weighted_rating' and calculate its value with `weighted_rating()`
        self.data['weighted_rating'] = self.data.apply(self.weighted_rating(self,self.data,m,C), axis=1)

        #Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
        tfidf = TfidfVectorizer(stop_words='english')

        #Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(self.data['Description'])
        # Compute the cosine similarity matrix
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        #Construct a reverse map of indices and movie titles
        self.indices = pd.Series(self.data.index, index=self.data['Title']).drop_duplicates()


    # Function that takes in movie title as input and outputs most similar movies
    def get_recommendations(self,title):
        # Get the index of the movie that matches the title
        idx = self.indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(self.cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        print('dupa')
        print(self.data['Title'].iloc[movie_indices])
        return self.data['Title'].iloc[movie_indices]




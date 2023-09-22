import scrapper
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import pickle

class Recommmender_Collab:

    def __init__(self):
        self.get_data()
        self.prepare_data()
        self.load_model()
        self.scr = scrapper.Scrapper()

    def get_data(self):
        self.df_users = pd.read_csv('ratings_data.csv')
        self.df_movies = pd.read_csv('movies_data.csv')
        self.all_shows_data = pd.read_csv('all_shows_data.csv')

    def prepare_data(self):
        self.df_users = self.df_users[['User','MovieID','Rating']]

        #Leaving only ratings for movies and users with high enough count
        v = self.df_users.MovieID.value_counts()
        self.df_users = self.df_users[self.df_users.MovieID.isin(v.index[v.gt(200)])]

        v = self.df_users.User.value_counts()
        self.df_users = self.df_users[self.df_users.User.isin(v.index[v.gt(50)])]  

        self.df_users = self.df_users.reset_index().pivot_table(index='MovieID',columns='User',values = 'Rating')
        self.df_users = self.df_users.fillna(0)

        self.movie_to_idx = {
            movie: i for i, movie in 
            enumerate(list(self.df_movies.set_index('MovieID').loc[self.df_users.index].Name))
        }

        self.user_matrix = csr_matrix(self.df_users.values)

    def save_model(self):
        


        model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)

        model_knn.fit(self.user_matrix)  

        model_pkl_file = "collab_model.pkl"  

        with open(model_pkl_file, 'wb') as file:  
            pickle.dump(model_knn, file)


    def load_model(self):   

        model_pkl_file = "collab_model.pkl"  

        with open(model_pkl_file, 'rb') as file:  
            self.model = pickle.load(file)


    def fuzzy_matching(self, mapper, fav_movie):
        """
        return the closest match via fuzzy ratio. If no match found, return None
        
        Parameters
        ----------    
        mapper: dict, map movie title name to index of the movie in data

        fav_movie: str, name of user input movie
        

        Return
        ------
        index of the closest match
        """
        match_tuple = []
        # get match
        for title, idx in mapper.items():
            ratio = fuzz.ratio(title.lower(), fav_movie.lower())
            if ratio >= 60:
                match_tuple.append((title, idx, ratio))
        # sort
        match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]
        if not match_tuple:
            return
        return match_tuple[0][1]

    def merge_dictionaries(self, dic1,dic2, rating):

        for key,value in dic2.items():
            if key in dic1.keys():
                dic1[key] = (dic1[key] + (rating * value)/10)
            else:
                dic1[key] = value
        return dic1 
    
    def make_recommendation_for_movie(self, model_knn, data, mapper, movie, n_recommendations):
        dic = {}
        
        #print('You have input movie:', fav_movie)
        #the function below is a helper function defined to check presence of Movie Name
        idx = self.fuzzy_matching(mapper, movie)
        
        num_rows, num_cols = data.shape


        if idx != None: 
            if idx <  num_rows :
                distances, indices = model_knn.kneighbors(data[idx], n_neighbors=n_recommendations+1)
                # get list of raw idx of recommendations
                raw_recommends = \
                    sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
                # get reverse mapper
                reverse_mapper = {v: k for k, v in mapper.items()}
                # print recommendations
                #print('Recommendations for {}:'.format(fav_movie))
                for i, (idx, dist) in enumerate(raw_recommends):
                    if idx in reverse_mapper.keys():
                        #print('{0}: {1}, with distance of {2}'.format(i+1, reverse_mapper[idx], dist))
                        dic[reverse_mapper[idx]] = dist
        
        return dic
    
    def make_recommendations(self,df):

        title_list = list(df.Name)
        recom_dic = {}

        for index,row in df.iterrows():
            dic = self.make_recommendation_for_movie(
                model_knn=self.model,
                data=self.user_matrix,
                movie=row.Name,
                mapper=self.movie_to_idx,
                n_recommendations=800)
            
            if dic != None:
                
                recom_dic=self.merge_dictionaries(recom_dic,dic, row.Rating)

        return sorted(recom_dic.items(),key = lambda x:x[1],reverse=True)
    
    def make_recommendations_for_user(self, user_name,n):
        user_df = self.scr.get_user_list(user_name)

        recommendations = self.make_recommendations(user_df)
        
        recom_df = pd.DataFrame(recommendations,columns=['Name','Recommendation Score']).sort_values(by='Recommendation Score',ascending=False).head(n)
        
        recom_df = recom_df.merge(self.all_shows_data[['Name','Country','Episodes','Score','Description','Genres']],on='Name')
        
        return recom_df









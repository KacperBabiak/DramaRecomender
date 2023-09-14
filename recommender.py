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

class Recommender:

    """
    Class used for getting information about shows and making recommendations

    ...


    Methods
    --------

    get_data()
        Reads data describing shows from a csv file

    data_to_csv()
        Gets describing all shows from a scrapper and writes it to a csv file
    
    insert_data_to_sql(user, password)
        Inserts data describing shows to a sql server
    
    clean_data(data)
        Deletes spaces from data and makes it all lower case

    recommend_prepare()
        Prepares data for giving recommendations. Its cleaned and transformed,  TF-DF matrix is being constructed.
        Computes a cosine similiriaty matrix and creates a map of indices and movie titles.

    get_recommendations(title, n)
        Gives n recommendations for a particular title


    get_similiar(title)
        Returns all shows similiar to a show with a given title

    get_recommendations_on_list(df)
        Gets recommendations for every show, assigns points and returns list of best overall recommended shows

        
    get_recommendations_for_user(user)
        Returns recommended shows for given user

    """

    def __init__(self):
        self.scr = scrapper.Scrapper()
        self.get_data()
        self.recommend_prepare()
        

    def get_data(self):
        self.data = pd.read_csv('all_shows_data.csv')
        self.data.drop(['Unnamed: 0','Name.1'],axis=1,inplace=True)

    def data_to_csv(self):
        
        self.data = self.scr.get_all_shows_data()
        self.data.to_csv('shows_data.csv',index=False)

    

    def clean_data(self, x ):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        else:
            if isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            else:
                return ''

    def make_cosine_sim_df(self,df):
        count = TfidfVectorizer(stop_words='english',lowercase=True)
        count_matrix = count.fit_transform(df)
        cosine_sim = cosine_similarity(count_matrix, count_matrix)
        return pd.DataFrame(cosine_sim)

    def recommend_prepare(self):
    
        # Apply clean_data function to your features.
        features = ['Screenwriter', 'Director']

        for feature in features:
            self.data[feature] = self.data[feature].apply(self.clean_data)

        #Construct the required TF-IDF matrix by fitting and transforming the data
        self.data = self.data.fillna('')

        #Construct a reverse map of indices and movie titles
        self.indices = pd.Series(self.data.index, index=self.data['Name']).drop_duplicates()
        

        
        
    def get_recommendations(self,title,n):


        cosine_sim_df_director = self.make_cosine_sim_df(self.data['Director'])
        cosine_sim_df_screenwriter = self.make_cosine_sim_df(self.data['Screenwriter'])
        cosine_sim_df_tag = self.make_cosine_sim_df(self.data['Tag'])
        cosine_sim_df_genres = self.make_cosine_sim_df(self.data['Genres'])
        cosine_sim_df_description = self.make_cosine_sim_df(self.data['Description'])

        a = self.data.copy().reset_index().drop('index',axis=1)
        index = a[a['Name']==title].index[0]


        similar_basis_metric_1 = cosine_sim_df_director[cosine_sim_df_director[index]>0][index].reset_index().rename(columns={index:'sim_1'})
        similar_basis_metric_2 = cosine_sim_df_screenwriter[cosine_sim_df_screenwriter[index]>0][index].reset_index().rename(columns={index:'sim_2'})
        similar_basis_metric_3 = cosine_sim_df_tag[cosine_sim_df_tag[index]>0][index].reset_index().rename(columns={index:'sim_3'})
        similar_basis_metric_4 = cosine_sim_df_genres[cosine_sim_df_genres[index]>0][index].reset_index().rename(columns={index:'sim_4'})
        similar_basis_metric_5 = cosine_sim_df_description[cosine_sim_df_description[index]>0][index].reset_index().rename(columns={index:'sim_5'})

        similar_df = similar_basis_metric_1.merge(similar_basis_metric_2,how='left').merge(similar_basis_metric_3,how='left').merge(similar_basis_metric_4,how='left').merge(similar_basis_metric_5,how='left').merge(a[['Name']].reset_index(),how='left')
        

        similar_df['sim'] = similar_df[['sim_1','sim_2','sim_3','sim_4','sim_5']].fillna(0).mean(axis=1)
        similar_df = similar_df[similar_df['index']!=index].sort_values(by='sim',ascending=False)
        
        return similar_df[['Name','sim']].head(n)

    


    def get_similiar(self,title):
        df=(self.data.loc[self.data['Name'] == title])
        
        return df['Similiar'].to_string(index=False)


    def get_recommendations_from_list(self,df):
        
        scores_dic = {}
        related_list = []
        for index,row in df.iterrows():
            if(row['Title'] in self.indices):
                #gets recommendations for every show in userlist
                recommended_list = self.get_recommendations(row['Title'],100)['Name'].values.tolist()
                
                
                #creating a list of shows related to recommended shows
                related_list.extend(self.get_similiar(row['Title']).split(";"))
                

                #creating a rating 
                for show in recommended_list:
                    if show in scores_dic:
                        
                        scores_dic[show]=scores_dic[show]+row['Rating']
                    else:
                        scores_dic[show]=row['Rating']
            
        #creating dataframes to show and deleting shows that were already watched
        rec_df = self.data.copy().drop(['Link','Number_of_rates','Tag','Similiar','Director','Screenwriter'],axis=1)
        rec_df = rec_df[~rec_df['Name'].isin(df['Title'])]
        rec_df['Score'] = 0

        rel_df = rec_df.copy()

        for show in scores_dic.keys():
            index=rel_df[rel_df['Name']==show].index

            if show in related_list:
                rel_df.loc[index,'Score'] = scores_dic[show]
            else:
                rec_df.loc[index,'Score'] = scores_dic[show]

        #deleting rows without a score
        rec_df.drop(rec_df[rec_df['Score'] == 0 ].index, inplace = True)
        rel_df.drop(rel_df[rel_df['Score'] == 0 ].index, inplace = True)

        #sorting
        rec_df.sort_values(inplace=True,by='Score',ascending=False)
        rel_df.sort_values(inplace=True,by='Score',ascending=False)

        

        

        return [rec_df,rel_df]

    def get_recommendations_for_user_old(self,user):
        user_list = self.scr.get_user_list(user)

        return self.get_recommendations_from_list(user_list)
    
    def get_recommendations_for_user(self,user,n):
        user_list = self.scr.get_user_list(user)

        user_df = self.data[self.data.Name.isin(user_list.Name)] 
        #adding sum of values as another row

        new_row = {'Name': 'Sum','Director': ' '.join(user_df.Director), 'Screenwriter': ' '.join(user_df.Screenwriter), 'Genres': ' '.join(user_df.Genres),'Description': ' '.join(user_df.Description),'Tag': ' '.join(user_df.Tag)}
        self.data.loc[len(self.data)] = new_row
        
        #getting recomnndations without title that were already seen or are related
        result = self.get_recommendations('Sum',n)
        result = result[~result['Name'].isin(user_list['Name'])]

        related =[]
        for index, row in user_df.iterrows():
            related.extend(row.Similiar.split(";"))

        result = result[~result['Name'].isin(related)]

        copy = self.data.copy().drop(['Link','Number_of_rates','Tag','Similiar','Director','Screenwriter'],axis=1)
        #result = pd.concat([result,copy],axis=1,join='inner')
        result = result.merge(copy,on='Name')

        result.sort_values(inplace=True,by='sim',ascending=False)
        #result.drop(['sim'],axis=1,inplace=True)
        return result

        


        







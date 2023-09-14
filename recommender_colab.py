import scrapper
import pandas as pd
import pickle
import tensorflow as tf
import tensorflow_recommenders as tfrs
import numpy as np
import movie_model

class Recommmender_Colab:

    def __init__(self):
        self.get_data()
        self.scr = scrapper.Scrapper()
        
    def predict_list(self, user_name, n):

        model = tf.keras.models.load_model('trfs.h5')

        # Create a model that takes in raw query features, and
        index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
        # recommends movies out of the entire movies dataset.
        index.index_from_dataset(
        tf.data.Dataset.zip((self.movies.batch(100), self.movies.batch(100).map(model.movie_model)))
        )

        # Get recommendations.
        _, titles = index(tf.constant([str(user_name)]))
        
        print('Top {} recommendations for user {}:\n'.format(n, user_name))
        for i, title in enumerate(titles[0, :n].numpy()):
            print('{}. {}'.format(i+1, title.decode("utf-8")))

    def get_data(self):
        self.movies_df = pd.read_csv('movies_data.csv') 
        self.ratings_df = pd.read_csv('ratings_data.csv')

    def create_model(self):
        self.prepare_data()
        self.model_fit()


    def prepare_data(self):
        self.ratings_df['User'] = self.ratings_df['User'].astype(str)

        self.ratings = tf.data.Dataset.from_tensor_slices(dict(self.ratings_df[['User', 'Movie_name', 'Rating']]))
        self.movies = tf.data.Dataset.from_tensor_slices(dict(self.movies_df[['Name']]))

        self.ratings = self.ratings.map(lambda x: {
            "Original_title": x["Movie_name"],
            "UserId": x["User"],
            "Rating": float(x["Rating"])
        })


        self.movies = self.movies.map(lambda x: x["Name"])

        tf.random.set_seed(42)
        shuffled = self.ratings.shuffle(1_000_000, seed=42, reshuffle_each_iteration=False)

        self.train = self.ratings.take(1323399)
        self.test = self.ratings.skip(1323399).take(330849)

        
        movie_titles = self.movies.batch(1_000)
        user_ids = self.ratings.batch(1_000).map(lambda x: x["UserId"])

        self.unique_movie_titles = np.unique(np.concatenate(list(movie_titles)))
        self.unique_user_ids = np.unique(np.concatenate(list(user_ids)))
        
    def model_fit(self):
        model = movie_model.MovieModel(rating_weight=1.0, retrieval_weight=1.0,
                                       unique_movie_titles = self.unique_movie_titles,
                                       unique_user_ids =self.unique_user_ids,
                                       movies =self.movies)
        
        model.compile(optimizer=tf.keras.optimizers.Adagrad(0.1))

        cached_train = self.train.shuffle(100_000).batch(1_000).cache()
        cached_test = self.test.batch(1_000).cache()

        model.fit(cached_train, epochs=3)

        metrics = model.evaluate(cached_test, return_dict=True)

        print(f"\nRetrieval top-100 accuracy: {metrics['factorized_top_k/top_100_categorical_accuracy']:.3f}")
        print(f"Ranking RMSE: {metrics['root_mean_squared_error']:.3f}")

        model.save_weights('tfrs.h5')


       




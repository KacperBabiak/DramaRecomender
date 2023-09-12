import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class Scrapper:

    def get_user_list(self,nickname):
        url = "https://mydramalist.com/dramalist/%s/completed" % (nickname)

        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="content_2")

        list_names=[]
        names = results.find_all("a", class_="title")

        for name in names:
            name=name['title']
            list_names.append(name)

        df = pd.DataFrame({'Name':list_names})

        list_ratings=[]
        ratings = results.find_all("span", class_="score")
        for rating in ratings:
            list_ratings.append(float(rating.text))

        df['Rating'] = list_ratings

        return df
    
    def get_page_number(self):
        url = "https://mydramalist.com/search?adv=titles&ty=68,77,83,86&so=relevance&page=1"
        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all(class_="page-item last")
       
        for result in results:
            link = result.find('a')['href']
            return int(link.split('=')[-1])
        
    def get_most_info(self,data, soup):
        info = ['Director','Screenwriter','Episodes','Country','Score']
        results = soup.find_all(class_="list-item p-a-0")

        for result in results:
            for inf in info:
                if inf in str(result):
                    info.remove(inf)
                    length = len(inf) + 2

                    if inf == 'Score':
                        data.update({'Score':result.text[length:length+3]}) 
                        data.update({'Number_of_rates':result.text[22:-7]})
                    else:
                        data.update({inf:result.text[length:]})
        
        return data

    def get_description(self,data, soup):
        results = soup.find_all(class_="show-synopsis")
        for result in results:
            try:
                data.update({'Description':result.find('span').text})
            except:
                data.update({'Description':''})
                
        
        return data
    
    def get_genres(self,data, soup):
        results = soup.find_all(class_="list-item p-a-0 show-genres")
        for result in results:
            data.update({'Genres' :result.text[8:]})
        
        return data
    
    def get_tags(self,data, soup):

        tags=[]
        results = soup.find_all(class_="list-item p-a-0 show-tags")
        
        for result in results:
            spans = result.find_all('span')
            for span in spans:
                tag = span.find('a', class_= 'text-primary')
                tags.append(tag.text)

        sep = ' '
        tags = sep.join(tags)    
        data.update({'Tag' :tags})
        
        return data
    
    def get_similiar(self,data,soup):
        similiar=[]
        results = soup.find_all(class_="list-item p-a-0 m-b-sm related-content")
        
        for result in results:
            titles = result.find_all('div')
            
            for title in titles:
                sim = title.find('a')
                similiar.append(sim.text)

        sep = ';'
        similiar = sep.join(similiar)    
        data.update({'Similiar' :similiar})
        
        return data


        
    def get_show_data(self,link,name):
        url = 'https://mydramalist.com%s' % link
        
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        
        data = {'Name':name}
        
        data = self.get_most_info(data,soup)
        data = self.get_description(data,soup)
        data = self.get_genres(data,soup)
        data = self.get_tags(data,soup)
        data = self.get_similiar(data,soup)

        return data



    def get_show_list(self,**kwargs):

        url = "https://mydramalist.com/search?adv=titles&ty=68,77,83,86&so=relevance&page=%s"
        df= pd.DataFrame(columns=['Name','Link'])

        if  'pages' in kwargs:
            number_of_pages = kwargs['pages']
        else:
            number_of_pages = self.get_page_number()

        for i in range(1,number_of_pages+1):
            page_url = url % (i)
            page = requests.get(page_url)

            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find_all(class_="text-primary title")

            
            for r in results:
                list_row = [r.find('a').text,r.find('a')['href']]
                df.loc[len(df)] = list_row

        return df
    
    def get_all_shows_data(self):
        df = self.get_show_list()
        df2 = pd.DataFrame()

        for index,row in df.iterrows():
            dic = self.get_show_data(row['Link'],row['Name'])
            df_dict = pd.DataFrame.from_dict([dic])
            
            df2 = pd.concat([df2,df_dict])
            
        df.reset_index(inplace=True, drop=True)   
        df2.reset_index(inplace=True, drop=True)  
        df = pd.concat([df,df2],axis=1)
        print(df)
        return df

            
        





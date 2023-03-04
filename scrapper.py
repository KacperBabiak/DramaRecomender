import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class scrapper:

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

        df = pd.DataFrame({'Title':list_names})


        ratings = results.find_all("span", class_="score")
        df['Rating'] = ratings

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
            data.update({'Description':result.find('span').text})
        
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

            
        data.update({'Tag' :tags})
        
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


        print(data)



    def get_show_list(self):

        url = "https://mydramalist.com/search?adv=titles&ty=68,77,83,86&so=relevance&page=%s"
        df= pd.DataFrame(columns=['Name','Link'])

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
            
        





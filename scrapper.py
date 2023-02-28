import requests
from bs4 import BeautifulSoup
import pandas as pd

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
        
    def get_show_data(link):
        url = 'https://mydramalist.com%s' % link

        df= pd.DataFrame(columns=['Name','Rating', 'Number_of_rates','Description', 'Director',
                                  'Screenwriter','Genre','Tags','Episodes_number','Country'])
        
        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all(class_="text-primary title")

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
            
        





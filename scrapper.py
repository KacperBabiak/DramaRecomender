import requests
from bs4 import BeautifulSoup
import pandas as pd

class scrapper:

    def getUserList(self,nickname):
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

    def getShowList(self):

        url = "https://mydramalist.com/search?adv=titles&ty=68,77,83,86&so=relevance&page=%s"

        for i in range(1,25):
            page_url = url % (i)
            print(page_url)
            page = requests.get(page_url)

            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find_all("h6", class_="text-primary title")
            results = results.find_all("a")
            list_links=[]

            #for result in results:
            #    link=result['a']
            #    list_links.append(link)



            df = pd.DataFrame({'links':results})
            print(df)
            return df





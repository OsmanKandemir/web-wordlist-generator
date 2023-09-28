
import requests,sys,os,re,tldextract,argparse,random
from urlextract import URLExtract
from multiprocessing import Pool
import threading, queue


from bs4 import (
                MarkupResemblesLocatorWarning,
                XMLParsedAsHTMLWarning,
                BeautifulSoup
                )

from wordlistGenerator.functions import	(
                        MultiProcessingTasks,
                        EmailIndicator,
                        Eliminate,
                        Merge,
                        bcolors,
                        RegX
                        )



from wordlistGenerator.log import (
                worktime,
                msg
                )

from wordlistGenerator.V1Finder import  (

                            GetPossibleSensitiveInformation,
                            GetEmails,
                            ReadData,
                            RemoveData
                            )   


import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print(f"""{bcolors.OKGREEN}

        __          __           _ _ _     _    _____                           _             
        \ \        / /   WEB    | | (_)   | |  / ____|                         | |            
         \ \  /\  / /__  _ __ __| | |_ ___| |_| |  __  ___ _ __   ___ _ __ __ _| |_ ___  _ __ 
          \ \/  \/ / _ \| '__/ _` | | / __| __| | |_ |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
           \  /\  / (_) | | | (_| | | \__ \ |_| |__| |  __/ | | |  __/ | | (_| | || (_) | |   
            \/  \/ \___/|_|  \__,_|_|_|___/\__|\_____|\___|_| |_|\___|_|  \__,_|\__\___/|_|   v1.0
                                                                                    
        Author : OsmanKandemir

{bcolors.ENDC}""")

class GeneratorException(Exception):
    """
    Generator exception class
    """
    def __init__(self, message):
        """
        GeneratorException class constructor
        :param info: string
        """
        self.info_ = info

        Exception.__init__(self, '%s' % (self.info_))


class LinkExtractor(object):

    def __init__(self,urls:list,worktime:str,proxy_server:str,agent:str,prnt:bool):

        """
        Link Extractor main class
        :param urls_: list
        :param worktime_: str
        :proxy_server_: dict
        :param proxy_server_ : dict or None
        :param prnt_ : True or None

        """
        
        self.urls_:list = urls
        self.worktime_:str = worktime
        self.proxy_server_:dict or None =  {'http': 'http://' + proxy_server} if proxy_server else None
        self.agent_:dict =  {'User-agent' : agent if agent else 'Mozilla/5.0'}
        self.prnt_:True or None = prnt

    
    def Crawling(self,urls:str) -> list:

        """
            Scrape target domain.

        """
        extractor = URLExtract()
        try:

            grab = requests.get(urls,proxies=self.proxy_server_,headers=self.agent_,timeout=(5,5),verify=False)
            if grab.status_code == 200:
                soup = BeautifulSoup(grab.content, 'html.parser',from_encoding="iso-8859-1")
                AllUrls = []
                GetPossibleSensitiveInformation(grab.text,self.worktime_)
                GetEmails(grab.text,self.worktime_)
                for link in soup.find_all(['a', 'link','script','base','form','area']):
                    if 'href' in link.attrs:
                        data = link.attrs['href']
                    if 'action' in link.attrs:
                        data = link.attrs['action']
                    if 'src' in link.attrs:
                        data = link.attrs['src']
                    if 'ping' in link.attrs:
                        data = link.attrs['ping']
                    try:
                        if extractor.find_urls(data):
                            if not Eliminate(data):AllUrls.append(data)
                        if data.startswith("/"):
                            ext = tldextract.extract(urls)
                            if not Eliminate(urls+data):
                                if ext.subdomain:
                                    AllUrls.append("http://" + ext.subdomain + "." + ext.domain + "." + ext.suffix + data)
                                else:
                                    AllUrls.append("http://"+ ext.domain + "." + ext.suffix + data)
                            else:
                                continue
                        else:
                            continue
                    except Exception:
                        continue
                        
                return list(set(AllUrls))
            elif grab.status_code in [500,502,503,504]:
                msg(f"{bcolors.OKBLUE}Connection Error{bcolors.ENDC}")
            else:
                pass
        except ConnectionError as Error:
            msg(f"{bcolors.OKBLUE}{Error.__class__.__name__}{bcolors.ENDC}")
            pass
        except Exception as Error:
            pass
        

    def Start(self,url:str,results_queue:queue.Queue):
        
        """
            Collect URLs for targets domains.

        """

        Tst = []
        msg(f"{bcolors.OKBLUE}Web-Wordlist-Generator is pulling to static links from target.{bcolors.ENDC}")
        try:
            res = self.Crawling(url)
            res = list(set(res))
            for i,z in zip(range(1,len(res)),res):
                res = self.Crawling(z)
                Tst.append(res)
            results_queue.put(Tst)
        except Exception as Error:
            msg(f"{bcolors.OKBLUE}Thread - Connection Error{bcolors.ENDC}")



    def Run(self) -> list:

        """
        
            MultiThread for the more target.
        
        """
        try:
            threads = []
            results_queue = queue.Queue()
            for i in self.urls_:
                t = threading.Thread(target=self.Start, args=(i, results_queue))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()

            results = []
            while not results_queue.empty():
                result = results_queue.get()
                results.append(result)
            
            del threads[:]
            
            d1,d2 = ReadData(self.worktime_,"GetPossibleSensitiveInformation"),ReadData(self.worktime_,"GetEmails")

            if self.prnt_:
                try:
                    for PRT1 in d1:print(PRT1)
                    for PRT2 in d2:print(PRT2)
                except:
                    pass
                
            return
                    
        except Exception as Error:
            msg(f"{bcolors.OKBLUE}Undefined domain or connection error.{bcolors.ENDC}")

    @property
    def urls(self) -> list:
        return self.urls_
    
    @property
    def worktime(self) -> str:
        return self.worktime_

    @property
    def proxy_server(self) -> dict or None:
        return self.proxy_server_
    
    @property
    def agent(self) -> dict or None:
        return self.agent_


    def __str__(self):
        return f"LinkExtractor"

    def __repr__(self):
        return 'LinkExtractor(urls_=' + str(self.urls_) + ' ,workspacename_=' + self.worktime_ + ' ,proxy_server_=' + self.proxy_server_ + ' ,agent_=' + self.agent_ +')'


def Crawl(domains, proxy_server = None, agent = None, prnt = None):
    
    """
        Configure worktime for separate each scan.
    
    """

    work = worktime()
    LinkExtractor(RegX(domains),work,proxy_server,agent, prnt).Run()

def STARTS():

    """
        Arguments Function.
    
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--domains", nargs='+', required="True", help="Input Targets. --domains sample.com sample2.com ")
    parser.add_argument("-p","--proxy", help="Use HTTP proxy. --proxy 0.0.0.0:8080")
    parser.add_argument("-a","--agent", help="Use agent. --agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' ")
    parser.add_argument("-o","--print", action='store_true', help="Print outputs on terminal screen. ")
    args = parser.parse_args()

    proxy = set()

    if args.domains:domains = [domain for domain in args.domains]
    proxy = args.proxy if args.proxy else None
    agent = args.agent if args.agent else None
    prnt = args.print if args.print else None
    
    Crawl(domains,proxy,agent,prnt)

if __name__ == "__main__":
    """
        What's Up bro ;)
    
    """
    STARTS()
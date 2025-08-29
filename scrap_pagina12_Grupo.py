
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
from scrapy.utils.response import open_in_browser
from scrapy.crawler import CrawlerProcess
from urllib import parse
from os import path
from scrapy.http.response.html import HtmlResponse
import multiprocessing
from typing import List

class NewsSpider(CrawlSpider):

    DOWNLOAD_HANDLERS = {
    'https': 'my.custom.downloader.handler.https.HttpsDownloaderIgnoreCNError',
    }

    name = 'crawler_pagina12'
    # solo descargar paginas desde estos dominios
    allowed_domains = ('www.pagina12.com.ar','pagina12.com.ar') ##Esto no es
    
    rules = (
        # Ejemplo de regla de scrapping:
        # solo bajar las paginas cuya url incluye "/secciones", pero no aquellas cuya url include "/catamarca12" o "/dialogo".
        # Ud. tiene que modificar esta regla para bajar solo indice + noticias de pagina 12.
        # scrappy normaliza las urls para no descargarlas 2 veces la misma pagina con distinta url.
        Rule(LinkExtractor(
            allow=r'.+\/\d{6}-.*',
            deny='.+/autores/.+',
            deny_domains=['auth.pagina12.com.ar'], 
            canonicalize=True,
            deny_extensions=['7z', '7zip', 'apk', 'bz2', 'cdr,' 'dmg', 'ico,' 'iso,' 'tar', 'tar.gz','pdf','docx', 'jpg', 'png', 'css', 'js']),
            callback='parse_response', 
            follow=True),
     )
    ##Modificacion 17/08 20.25hs: Se agregaron secciones "prohibidas" usando script scrap secciones.py
     
    # configuracion de scrappy, ver https://docs.scrapy.org/en/latest/topics/settings.html
    # la var de clase debe llamarse "custom settings"
    custom_settings = {
      # mentir el user agent // Modificado 22/8/2025 6.32hs
     'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
     'LOG_ENABLED': True,
     'LOG_LEVEL': 'INFO',
      # no descargar paginas mas alla de 1 link desde la pagina de origen
     'DEPTH_LIMIT': 2, ##hace que llegue la noticia
      # ignorar robots.txt (que feo eh) es una regla
     'ROBOTSTXT_OBEY': False,
      # esperar entre 0.5*DOWNLOAD_DELAY y 1.5*DOWNLOAD_DELAY segundo entre descargas
     'DOWNLOAD_DELAY': 1.5,
     'RANDOMIZE_DOWNLOAD_DELAY': True,
     'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def __init__(self, save_pages_in_dir='.', *args, **kwargs):
          super().__init__(*args, **kwargs)
          # guardar el directorio en donde vamos a descargar las paginas
          self.basedir = save_pages_in_dir
    
    def parse_response(self, response:HtmlResponse):
          """
          Este metodo es llamado por cada url que descarga Scrappy.
          response.url contiene la url de la pagina,
          response.body contiene los bytes del contenido de la pagina.
          """
          # el nombre de archivo es lo que esta luego de la ultima "/"
          html_filename = path.join(self.basedir,parse.quote(response.url[response.url.rfind("/")+1:]))
          if not html_filename.endswith(".html"):
              html_filename+=".html"
          print("URL:",response.url, "Pagina guardada en:", html_filename)
          # sabemos que pagina 12 usa encoding utf8
          with open(html_filename, "wt", encoding="utf-8") as html_file:
              html_file.write(response.body.decode("utf-8"))
          

def start_crawler(page_number:int, save_pages_in_dir:str, start_urls:List[str]): 
    crawler = CrawlerProcess()
    crawler.crawl(NewsSpider, save_pages_in_dir = save_pages_in_dir, start_urls = start_urls)
    crawler.start()


if __name__ == "__main__":
   DIR_EN_DONDE_GUARDAR_PAGINAS = "C:/Users/ivan_/OneDrive/Desktop/Maestria en Ciencia de Datos/Austral/WebMining/TP1/Articulosdescargados"
   if not path.exists(DIR_EN_DONDE_GUARDAR_PAGINAS): ##Agregado 22/08/2025 6.46PM
         print(f"ERROR: Directory {DIR_EN_DONDE_GUARDAR_PAGINAS} does not exist.")
         exit(-1)
   for page_number in range(3,50):
         # Ejecutar al crawler en un proceso separado, sino al 
         # volver a arrancar con la prox pagina de indice de noticias,
         # el crawler de scrappy da error. Esto es un fix para un problema particular de scrappy.
         print(page_number, "----------------------------")
         ##
         process = multiprocessing.Process(target=start_crawler, 
                                           args=(page_number, DIR_EN_DONDE_GUARDAR_PAGINAS, 
                                                 [f'https://www.pagina12.com.ar/secciones/economia/?page={page_number}'])) ##Cambiar aca
         process.start()
         process.join() ##page_number

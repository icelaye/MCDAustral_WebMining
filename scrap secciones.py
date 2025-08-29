import scrapy

class Pagina12Spider(scrapy.Spider):
    name = 'pagina12'
    start_urls = ['https://www.pagina12.com.ar']
    
    def parse(self, response):
        # Extraer todos los enlaces de secciones
        secciones = []
        
        # Buscar enlaces que contengan /secciones/
        for link in response.css('a[href*="/secciones/"]::attr(href)').getall():
            seccion = link.split('/secciones/')[-1]
            if seccion:
                secciones.append(f"/{seccion}")
        
        # Buscar enlaces directos a secciones principales
        for link in response.css('a[href^="/"]::attr(href)').getall():
            if '/' in link[1:] or any(char.isdigit() for char in link):
                continue
            seccion = link.strip('/')
            if seccion and seccion not in ['edicion-impresa', 'suscribite']:
                secciones.append(f"/{seccion}")
        
        # Eliminar duplicados y formatear
        secciones = sorted(list(set(secciones)))
        resultado = "|".join(secciones)
        
        print(f"\nSecciones encontradas:\n{resultado}")
        
        return {'secciones': resultado}

# Para ejecutar directamente
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    process.crawl(Pagina12Spider)
    process.start()
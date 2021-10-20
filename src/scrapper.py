#!/usr/bin/env python3
import requests
from requests.models import HTTPError
import lxml.html as html

class Scrapper():
    def __init__(self):
        self.LINIO = {
            'url': 'https://www.linio.com.co/search?scroll=&q=',
            'products': '/html/body/div[3]/main/div[1]/div[7]/div[2]/div/div',
            'titlo': '/html/body/div[3]/main/div[1]/div[7]/div[2]/div/div/a[1]/meta[1]/@content',
            'sku': '/html/body/div[3]/main/div[1]/div[7]/div[2]/div/div/a[1]/meta[2]/@content',
            'imageUrl': '/html/body/div[3]/main/div[1]/div[7]/div[2]/div/div/a[1]/meta[4]/@content',
            'descripcion': '/html/body/div[3]/main/div[1]/div[7]/div[2]/div/div/a[1]/meta[6]/@content'
        }

        self.MERCADOLIBRE ={
            'url': 'https://listado.mercadolibre.com.co/'
        }

        self.DIGITALTECNOLOGY = {
            'url': 'https://www.computadoresbogota.com/articulos/buscar_articulos.php?consulta=1&param_consulta=',
            'titulo': '/html/body/div[2]/div[2]/div[3]/table/tbody/tr/td[2]/div[1]/a/b',    
            'test': '/html/body/div[2]/div[2]/div[3]/table/tbody'
        }

    def getPage(self, pagina, busqueda=None, sku=None):
        """ Trae la pagina total de la busqueda hecha

        Args:
            pagina (String): Indica si se va hacer la busqueda en Mercado libre o en Linio
                ML: MercadoLibre
                LI: Linio
                DT: Digital Tecnology
            busqueda (String, optional): Es la busqueda que se quiere hacer en el sitio web. Defaults to None.
            sku (String, optional): Es el SKU que se quiere buscar en el sitio Web. Defaults to None.
        """
    
        if pagina == 'ML':
            try:
                query = self.separarGuion(busqueda)
                response = requests.get(self.MERCADOLIBRE['url']+query)
                if response.status_code==200:
                    pagina = response.content.decode('utf-8')
                    parsed = html.fromstring(pagina)
                else:
                    raise ValueError(f'Error: {response.status_code}')
            except ValueError as ve:
                print(ve)
            
        elif pagina == 'LI':
            try:
                query = self.separarMas(busqueda)
                response = requests.get(self.LINIO['url']+query)
                if response.status_code==200:
                    pagina = response.content.decode('utf-8')
                    parsed = html.fromstring(pagina)
                else:
                    raise ValueError(f'Error: {response.status_code}')
            except ValueError as ve:
                print(ve)

        elif pagina == 'DT':
            try:
                response = requests.get(self.DIGITALTECNOLOGY['url']+sku)
                if response.status_code==200:
                    pagina = response.content.decode('utf-8')
                    parsed = html.fromstring(pagina)
                else:
                    raise ValueError(f'Error: {response.status_code}')
            except ValueError as ve:
                print(ve)
        else:
            raise ValueError(f'{pagina} no es valido')
            
        return parsed

    def getDescripcion(self, pag, pagina) :
        # Primer paso - get Los productos resultados de la busqueda
        if pagina == 'LI':
            titulos = pag.xpath(self.LINIO['descripcion'])
            print(titulos[3])

        elif pagina == 'DT':
            pass

    def getPrecio(self, pagina, busqueda=None, sku=None):
        pass

    def getImagen(self, pagina, busqueda=None, sku=None):
        pass
        
    def getTitle(self, pag, pagina):
        if pagina == 'DT':
            title = pag.xpath(self.DIGITALTECNOLOGY['test'])
            print(title)

    def separarMas(self, busqueda):
        """ Recibe una cadena de caracteres y crea una nueva con cada
            palabra separada por un '+'

        Args:
            busqueda (String): Busqueda que se quiere transformar. 
                               Va a llegar todo el nombre del producto.

        Return:
            busqueda (String): Cadena transformada
        """ 
        arrayBusqueda = busqueda.split(',')
        busqueda = arrayBusqueda[0]
        busqueda = busqueda.replace(" ", "+")
        
        return busqueda

    def separarGuion(self, busqueda):
        """ Recibe una cadena de caracteres y crea una nueva con cada
            palabra separada por un '-'

        Args:
            busqueda (String): Busqueda que se quiere transformar. 
                               Va a llegar todo el nombre del producto.

        Return:
            busqueda (String): Cadena transformada
        """ 
        arrayBusqueda = busqueda.split(',')
        busqueda = arrayBusqueda[0]
        busqueda = busqueda.replace(" ", "-")
        
        return busqueda
    
if __name__ == '__main__':
    scrapper = Scrapper()
    #r = scrapper.getDescripcion(pagina='LI',busqueda='PC Lenovo M720S SFF Core i5-8500 Processor')
    pagina = scrapper.getPage('DT', sku="10SUS48F00")
    titulo = scrapper.getTitle(pagina, "DT")
    

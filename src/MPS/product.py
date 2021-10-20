#!/usr/bin/env python3

import requests
from src.authentication import Authentication
class Product:
    """ Clase tiene variables y metodos para llevar
        acabo las operaciones sobre los productos de MPS
    """

    def __init__(self):
        self.accessToken = Authentication.getAccessTokenMPS()
        self.gamingId = '11'
        self.componentsId = '11'
        self.cablesId = '19'
        self.consolasJuegosId = '8'
        self.url = "https://shopcommerce.mps.com.co:8081/api/Webapi/VerCatalogo"

        self.headers = {
            'Content-Type': 'application/json',
            'X-DISPONIBILIDAD': '1',
            'X-DESCUENTO': '0',
            'X-CATEGORIA': '',
            'Authorization': 'Bearer '+str(self.accessToken)
        }



    def getProductsGaming(self):
        """ Trae todos los productos de MPS
        """
        self.headers['X-CATEGORIA'] = self.gamingId
        try:
            req = requests.post(self.url, headers=self.headers).json()
        except:
            print(f'No se pudieron traer los productos gaming de MPS')
        else:
            print(f'Se trajeron los productos exitosamente')

        
        return req

    def getProductsConsola(self):
        """ Trae todos los productos de MPS
        """
        self.headers['X-CATEGORIA'] = self.consolasJuegosId
        try:
            req = requests.post(self.url, headers=self.headers).json()
        except:
            print(f'No se pudieron traer los productos gaming de MPS')
        else:
            print(f'Se trajeron los productos exitosamente')

        
        return req

    def getProductsCables(self):
        """ Trae todos los productos de MPS
        """
        self.headers['X-CATEGORIA'] = self.cablesId
        try:
            req = requests.post(self.url, headers=self.headers).json()
        except:
            print(f'No se pudieron traer los productos gaming de MPS')
        else:
            print(f'Se trajeron los productos exitosamente')

        
        return req
    
    def getProductsComponentes(self):
        """ Trae todos los productos de MPS
        """
        self.headers['X-CATEGORIA'] = self.componentsId
        try:
            req = requests.post(self.url, headers=self.headers).json()
        except:
            print(f'No se pudieron traer los productos gaming de MPS')
        else:
            print(f'Se trajeron los productos exitosamente')

        
        return req
    
   
    

if __name__ == '__main__':
    product = Product()
    r = product.getProductsConsola()
    print(r)
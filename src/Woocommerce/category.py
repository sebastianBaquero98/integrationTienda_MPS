#!/usr/bin/env python3
from os import access
import unicodedata
from src.authentication import Authentication
import requests

class Category:
    """ Clase se encarga de las operaciones sobre
        las categorias de Tienda Itelco
    """

    def __init__(self):
        self.api = Authentication.generateAPIWoo()
        self.accessToken = Authentication.getAccessTokenWoo()

    def getXId(self, idCategory):
        """ Trae información sobre la cateogria usando el id

        Args:
            idCategory (int): Id de la categoria a buscar

        Return:
            result (Dictionary): Diccionario con la información de la categoria
        """
        result = ''
        try:
            result = self.api.get(f'products/categories/{idCategory}').json()
        except:
            print(f'No se pudo traer la categoria {idCategory}')
        else:
            print(f'Se pudo traer la información de categoria {idCategory}')
        
        return result

    def getAll(self):
        """ Trae todas las categorias de la tienda

        Return:
            result (Dictionary): Diccionario con información de todas las categorias
        """
        url = "https://www.tiendaitelco.com/wc-api/v3/products/categories?[limit]=-1"
        
        headers = {
            'Authorization': self.accessToken,
        }
        result = ''
        try:
            result = requests.get(url,headers=headers).json()
        except:
            print(f'No se pudo traer todas las categorias')
        else:
            print(f'Se trajo la información de todas las categorias')

        return result

    def deleteXId(self, idCategory):
        """ Elimina la cateogria usando el id

        Args:
            idCategory (int): Id de la categoria a buscar

        Return:
            result (Dictionary): Diccionario con la información de la categoria eliminada
        """

        try:
            result = self.api.delete(f'products/categories/{idCategory}').json()
        except:
            print(f'No se pudo eliminar la cateogira {idCategory}')
        else:
            print(f'Se elimino la categoria {idCategory}')
        
        return result

        
    def getIdXMPS(self, nameCategory, categories):
        """ Encuentra el id de la categoria en la tienda usando un diccionario de categorias

        Args:
            nameCategory (String): Nombre de la categoria a buscar
            categories (Dictionary): Llave es categoria MPS y el valor es el id de la categoria en la Tienda

        Return:
            answerId (int): Es el id de la categoria en la tienda
        """
        answerId = 0
        if nameCategory in categories.keys():
            answerId = categories[nameCategory]
        
        return answerId

if __name__ == '__main__':
    cate = Category()
    #r = cate.getXId(634)
    #print(r)
    r = cate.getAll()
    print(r)
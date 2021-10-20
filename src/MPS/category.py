from authentication import Authentication
import json
import requests

class Category:
    """ Clase encargada de realizar las
        operaciones sobre las categorias
        de MPS
    """
    def __init__(self):
        pass

    def getCategorias(self):
        accessToken = Authentication.getAccessTokenMPS()
        url = "https://shopcommerce.mps.com.co:8081/api/WebApi/VerCategoria"
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + accessToken,
            'cache-control': 'no-cache'
        }
        try:
            req = requests.get(url, headers=headers).json()
            print(req)
        except:
            print("No se pudo traer las categoiras de MPS")
        else:
            print("Se trajeron las categorias de MPS")
            print("La cantidad de categorias es: "+str(len(req)))

        return req

    
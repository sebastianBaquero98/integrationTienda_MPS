#!/usr/bin/env python3
import requests
import json
from src.authentication import Authentication
from src.Woocommerce.category import Category
from src.scrapper import Scrapper
import pprint

class Product:
    """ Clase encargada de realizar operaciones
        sobre los products de la Tienda (Woocommerce)
    """
    def __init__(self):
        self.api = Authentication.generateAPIWoo()
        self.url = "https://www.tiendaitelco.com/wc-api/v3/products?filter[limit]=-1"
        self.baseUrl = 'https://www.mps.com.co/images/Productos/'
        with open("/Users/user/OneDrive - Universidad de los Andes/Tienda Itelco/MpsWoocommerceIntegration/src/static/listaCategoriasGamer.txt", encoding="utf-8") as myFile:
            myFileReads = myFile.read()

        # Diccionario con llave categoria MPS y valor id en Tienda Itelco
        self.categoriesWC = json.loads(myFileReads)
        self.categoryManager = Category()
        #self.scrapper = Scrapper()
        self.product = {
            "dimensions": {"length": "", "width": "", "height": ""},
            "manage_stock": True,
            "sku": "",
            "name": "",
            "type": "simple",
            "regular_price": "",
            "stock_quantity": 0,
            "description": "",
            "short_description": "",
            "weight": "",
            "categories": [
                {   
                    "id": 0
                }
            ],
            "images": [
                {
                    "src": ""
                }
            ],
            "purchase_note": ""
        }

    def getAll(self):
        """ Trae todos los productos de Tienda Itelco (Woocommerce)

        Returns:
            Dictionary: Dictionario con todos los productos
        """
        accessToken = Authentication.getAccessTokenWoo()
        print(self.url)
        print(accessToken)
        headers = {
            'Authorization': accessToken
        }
        result = ""

        try:
            result = requests.get(self.url, headers=headers).json()
        except:
            print('No se pudo traer los productos de Tienda Itelco')
        else:
            print('Los productos se trajeron satisfactoriamente')
        
        return result

    def getXId(self, idProduct):
        """ Trae un producto con el id

        Args:
            idProduct (int): Id del producto a traer

        Returns:
            Dictionary: Diccionario con toda la información del producto solicitado
        """
        try:
            result = self.api.get(f'products/{idProduct}').json()
        except:
            print(f'No se pudo traer el producto {idProduct} de Tienda Itelco')
        else:
            print(f'El producto {idProduct} se trajo satisfactoriamente')
        
        return result

    def imgExists(self, imgUrl):
        """ Mira si la imagen existe en la base de datos de MPS

        Args:
            imgUrl (String): URL de la imagen a verificar
        """
        
        try:
            result = requests.get(imgUrl)
            if result.status_code == 404:
                return False
        except:
            return False

        return True

    def addAtribute(self, nameAtibute):
        data = {
        "name": nameAtibute,
        "slug": nameAtibute,
        "type": "select",
        "order_by": "menu_order",
        "has_archives": True
        }
        self.api.post("products/attributes", data).json()

    
    def create(self, mpsProduct):
        """ Crea un producto en Tienda Itelco. 
    
        Args:
            mpsProduct (Dictionary): Dictionario con información del producto que se creará

        Return:
            Dictionary: Diccionario con información del producto creado
        """
        self.product['sku'] = mpsProduct['PartNum']
        self.product['name'] = mpsProduct['Name']
        self.product['stock_quantity'] = mpsProduct['Quantity']
        self.product['short_description'] = mpsProduct['MarcaHomologada']
        self.product['purchase_note'] = mpsProduct['color']
        precios = self.setPrice(mpsProduct)
        self.product['sale_price'] = str(precios[0])
        self.product['regular_price'] = str(precios[1])

        # Se recorrera todas las llaves del producto para agregarlos a product
        for key in mpsProduct:
            # ------------- CATEGORIA -------------
            if key == 'Categoria':
                categorias = []
                id = self.categoryManager.getIdXMPS(mpsProduct[key], self.categoriesWC)
                dict_categoria = {'id': id}
                categorias.append(dict_categoria)
                self.product['categories'] = categorias

            # ------------- WEIGHT -------------
            if key == 'weight':
                weightStr = str(mpsProduct[key])
                self.product['weight'] = weightStr
            
            # ------------- WIDTH -------------
            if key == "width":
                width = mpsProduct[key]
                widthStr = str(width)
                self.product['dimensions']['width'] = widthStr

            # ------------- HEIGHT -------------
            if key == "height":
                height = mpsProduct[key]
                heightStr = str(height)
                self.product['dimensions']['height'] = heightStr
            
            # ------------- DEPTH -------------
            if key == "depth":
                depth = mpsProduct[key]
                depthStr = str(depth)
                self.product['dimensions']['length'] = depthStr

            # ------------- DESCRIPTION -------------
            if key == "Description":
                if mpsProduct[key]:
                    self.product['description'] = mpsProduct[key]

            # ------------- IMAGES -------------
            if key == "Imagenes":
                img = []
                temp = {'src': ''}
                if mpsProduct[key][0] == "":
                    img.append(temp)
                else:
                    if self.imgExists(mpsProduct[key][0]) == True:
                        temp['src'] = mpsProduct[key][0]
                        img.append(temp)
                    if self.imgExists(mpsProduct[key][1]) == True:
                        temp['src'] = mpsProduct[key][1]
                        img.append(temp)
                    if self.imgExists(mpsProduct[key][2]) == True:
                        temp['src'] = mpsProduct[key][2]
                        img.append(temp)
                    if self.imgExists(mpsProduct[key][3]) == True:
                        temp['src'] = mpsProduct[key][3]
                        img.append(temp)

                self.product['images'] = img

        result = ""
        
        try:
            result = self.api.post("products", self.product).json()
        except:
            print(f'Producto {mpsProduct["PartNum"]} creado sin exito')
        else:
            print(f'Producto {mpsProduct["PartNum"]} creado exitosamente')
            
        return result

    def deleteXId(self, idProduct):
        """ Borra un producto de Tienda Itelco

        Args:
            idProduct (int): Id del producto
        
        Return:
            result (Dictionary): Diccionario con la información del elemento eliminado
        """
        result = ""
        try:
            result = self.api.delete(f'products/{idProduct}', params={"force": True}).json()
        except:
            print(f'No se pudo eliminiar el producto {idProduct}')
        else:
            print(f'Se pudo elimino el producto {idProduct}')
        
        return result

    def update(self, idProduct, data):
        """ Actualiza un producto de la tienda dado su id

        Args:
            idProduct (String): Id del producto a actualizar
            data (Dictionary): Diccionario con información a cambiar
        """
        result = ""
        try:
            result = self.api.put(f'products/{idProduct}', data).json()
        except:
            print(f'No se pudo actualizar el producto {idProduct}')
        else:
            print(f'Se actualizo exitosamente el producto {idProduct}')

        return result

    def deleteAll(self):
        t = self.getAll()
        for product in t['products']:
            self.deleteXId(product['id'])
            print(f'Se elimino el producto {product["id"]}')

    
            

    def setPrice(self, mpsProduct):
        """ Decide el precio regular y precio con desceunto del producto
            En la tienda se manejarán dos precios
                - precioDescuento: Es el precio al que se le va a ofrecer al cliente final
                - precioSinDesceunto: Es el precio 'original' del producto (10% mas que precioDescuento)

        Args:
            mpsProduct (Dictionary): Diccionario con la información del producto

        Returns:
            ans (Array): Es un arreglo de numeros con el precioDescuento y precioSinDescuento (EN ESE ORDEN)
        """
        ans = []
        uvt = 36308
        precioMPS = mpsProduct['precio']
        precioDescuento = round(precioMPS / 0.90, -3)
        # Verifica si es gravado o exlcuido de IVA
        if mpsProduct['TributariClassification'] == 'EXCLUIDO':
            if mpsProduct['Familia'] == 'Celulares' or mpsProduct['Familia'] == 'Tablets':
                limite = 22 * uvt
                if mpsProduct['precio'] >= limite:
                    # Se tiene que pagar IVA
                    precioDescuento = round(precioDescuento * 1.19, -3)
                    precioSinDescuento = round(precioDescuento * 1.10, -3)
                    ans.append(precioDescuento)
                    ans.append(precioSinDescuento)
                else:
                    # No se tiene que pagar IVA
                    precioSinDescuento = round(precioDescuento * 1.10, -3)
                    ans.append(precioDescuento)
                    ans.append(precioSinDescuento)

            elif mpsProduct['Familia'] == 'Pc' or mpsProduct['Familia'] == 'Portatiles':
                limite = 50 * uvt
                if mpsProduct['precio'] >= limite:
                    # Se tiene que pagar IVA
                    precioDescuento = round(precioDescuento * 1.19, -3)
                    precioSinDescuento = round(precioDescuento * 1.10, -3)
                    ans.append(precioDescuento)
                    ans.append(precioSinDescuento)
                else:
                    # No se tiene que pagar IVA
                    precioSinDescuento = round(precioDescuento * 1.10, -3)
                    ans.append(precioDescuento)
                    ans.append(precioSinDescuento)

            else:
                precioSinDescuento = round(precioDescuento * 1.10, -3)
                ans.append(precioDescuento)
                ans.append(precioSinDescuento)

        elif mpsProduct['TributariClassification'] == 'GRAVADO':
            # Sumamos el IVA
            precioDescuento = round(precioDescuento * 1.19, -3)
            precioSinDescuento = round(precioDescuento * 1.10, -3)
            ans.append(precioDescuento)
            ans.append(precioSinDescuento)

        return ans

    def createListIds(self):
        products = self.getAll()
        productsDict = {}
        for index in range(len(products['products'])):
            for key in products['products'][index]:
                    id = products['products'][index]['id']
                    sku = products['products'][index]['sku']
                    productsDict.update({sku: id})
                    break

        with open("/Users/user/OneDrive - Universidad de los Andes/Tienda Itelco/MpsWoocommerceIntegration/src/static/listaIds.txt", mode="w", encoding="utf-8") as my_file: 
            my_file.write(json.dumps(productsDict))


if __name__ == '__main__':
    productManager = Product()
    #r = productManager.getAll()
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(r)
    #print(len(r))
    #print(type(r))
    #r = productManager.getAll()
    #print(r)
    productManager.deleteAll()
    #r = productManager.getXId(34668)
    p = {
        "PartNum": "ABCDEF",
        "Sku": "ABCDEF",
        "Familia": "AUDIO Y VIDEO",
        "Categoria": "Audio Portátil",
        "Name": "Este es un producto de prueba",
        "Description": "Descripción de producto de prueba",
        "Marks": "ELTEST",
        "Salesminprice": 65.27,
        "Salesmaxprice": 68.28,
        "precio": 245429.0,
        "CurrencyDef": "USD",
        "Quantity": 20,
        "TributariClassification": "GRAVADO",
        "NombreImagen": "984-001547.jpg",
        "Descuento": 0.0,
        "shipping": -1,
        "condition": "",
        "category": "",
        "color": "",
        "width": 0.0,
        "height": 0.0,
        "depth": 0.0,
        "dimensions_unit": "",
        "weight": 0.0,
        "weight_unit": "",
        "shipping_width": 0.0,
        "shipping_height": 0.0,
        "shipping_depth": 0.0,
        "ListaProductosBodega": [
            {
                "Bodega": "BCOTA",
                "NombreBodega": "BCOTA",
                "Cantidad": 20
            }
        ]
    }

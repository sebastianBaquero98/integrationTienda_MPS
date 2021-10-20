#!/usr/bin/env python3
from MPS.product import Product as MPSProduct
from Woocommerce.product import Product as WOOProduct
import json
def runUpdate():
    """ Es el metodo que se correr cuando
        se quiere actualizar la tienda (Cada hora)
    """
    MPSProductManager = MPSProduct()
    WOOProductManager = WOOProduct()


    # Diccionario de products de MPS [Solo va a traer los gaming]
    mpsProductsGaming = MPSProductManager.getProductsGaming()
    mpsProductsCables = MPSProductManager.getProductsCables()
    mpsProductsConsola = MPSProductManager.getProductsConsola()
    mpsProductsGaming = mpsProductsGaming['listaproductos']
    mpsProductsCables = mpsProductsCables['listaproductos']
    mpsProductsConsola = mpsProductsConsola['listaproductos']

    # Un arreglo con los skus de los productos de MPS
    skus =[] 

    # Se agregan los productos de las categorias necesitadas en un arreglo
    todoProducts = mpsProductsGaming
    for product in mpsProductsConsola:
        todoProducts.append(product)
    for product in mpsProductsConsola:
        todoProducts.append(product)
    
    for product in todoProducts:
        sku = product['PartNum']
        skus.append(sku)

    with open("/Users/user/OneDrive - Universidad de los Andes/Tienda Itelco/MpsWoocommerceIntegration/src/static/listaIds.txt", encoding="utf-8") as my_file:
            my_file_read = my_file.read()

    # Diccionario (llave: SKU del producto, valor: Codigo interno de woocommerce del producto)
    productsWC = json.loads(my_file_read)

    # --------------- CASO 1 ---------------
    """ Existe el producto en la tienda, pero en el listado actualizado de MPS no esta.
        Por lo tanto, el producto se actualizará poniendo el inventario en 0
    """
    for key in productsWC.keys():
         if key not in skus:
            print("Entro Caso 1")
            data = {"stock_quantity": 0}
            WOOProductManager.update(productsWC[key], data)
    
    for mpsProduct in todoProducts:
        # --------------- CASO 2 ---------------
        """ Existe el producto en la tienda y en el listado actualizado de MPS.
            Por lo tanto, en la tienda se actualizará el precio y el inventario
        """
        
        if mpsProduct['Sku'] in productsWC.keys():
            print("Entro Caso 2")
            # ----- PRECIO -----
            precios = WOOProductManager.setPrice(mpsProduct)
            precioSale = precios[0]
            precioRegular = precios[1]

            # ----- QUANTITY -----
            stock = mpsProduct['Quantity']

            # ------ UPDATE ------
            data = {
                "stock_quantity": stock,
                "regular_price": precioRegular,
                "sale_price": precioSale
            }
            idWoo = productsWC[mpsProduct['Sku']]
            WOOProductManager.update(idWoo,data)
           

                
        # --------------- CASO 3 ---------------
        """ Existe el producto en la lista actualizada de MPS, tiene inventario mayor a 0 y no existe en la tienda
            Por lo tanto, se creará el producto en la tienda y se escribira en el archivo para mantenerlo actualizado
        """
        if mpsProduct['Sku'].strip() not in productsWC.keys():
            print("Entro Caso 3")
            productoNuevo = WOOProductManager.create(mpsProduct)
            idNuevo = productoNuevo['id']
            productsWC[mpsProduct['Sku']] = idNuevo

    # El archivo se creara con los nuevos productos
    with open("/Users/user/OneDrive - Universidad de los Andes/Tienda Itelco/MpsWoocommerceIntegration/src/static/listaIds.txt", mode= "w", encoding="utf-8") as my_file:
        my_file.write(json.dumps(productsWC))
                
def runTest():

    # ------------------ INICIO TEST -----------------
    pTest = {
        "PartNum": " 2HL44AA#ABM",
        "Sku": " 2HL44AA#ABR",
        "Familia": "PCS_old",
        "Categoria": "All In One Consumo",
        "Name": "AIO HP PAVILION A9 MEMORIA 4GBDISCO 1TB  PANTALLA  27 Win10 BLANCO",
        "Description": "AIO HP PAVILION A9 MEMORIA 4GBDISCO 1TB  PANTALLA  27 Win10 BLANCO ",
        "Marks": "HPPCSCONSUMO",
        "Salesminprice": 1750715.47,
        "Salesmaxprice": 1829399.31,
        "precio": 1750715.0,
        "CurrencyDef": "COP",
        "Quantity": 0,
        "TributariClassification": "EXCLUIDO",
        "NombreImagen": "2HL44AAABR.jpg",
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
        "ListaProductosBodega": []
    }

    test = {"ABCD": 34, "EFGH": 35}
    if " ABCD" not in test.keys():
        print('Encontre el problema papa')

    # ------------------ FIN TEST -----------------

def runInit():
    """ Se corre inicialmente
        Es la primera carga de prodcutos de la tienda
    """
    MPSProductManager = MPSProduct()
    WOOProductManager = WOOProduct()

    # Diccionario de products de MPS [Solo va a traer los gaming]
    mpsProductsGaming = MPSProductManager.getProductsGaming()
    mpsProductsCables = MPSProductManager.getProductsCables()
    mpsProductsConsola = MPSProductManager.getProductsConsola()
    mpsProductsGaming = mpsProductsGaming['listaproductos']
    mpsProductsCables = mpsProductsCables['listaproductos']
    mpsProductsConsola = mpsProductsConsola['listaproductos']

    # Se agregan los productos de las categorias necesitadas en un arreglo
    todoProducts = mpsProductsGaming
    for product in mpsProductsConsola:
        todoProducts.append(product)
    for product in mpsProductsCables:
        todoProducts.append(product)

    # Crea los atributos
    
    # Recorre los productos creandolos en la tienda y escribiendo en el archivo
    p = {}
    for mpsProduct in todoProducts:
        if mpsProduct['Sku'] not in p:
            # No esta repetido entonces crear
            try:
                productoNuevo = WOOProductManager.create(mpsProduct)
                idNuevo = productoNuevo['id']
            except:
                print(f'Error en producto {mpsProduct["Sku"]}')
                continue
            else:
                p[mpsProduct['Sku']] = idNuevo
                print(p)

    with open("/Users/user/OneDrive - Universidad de los Andes/Tienda Itelco/MpsWoocommerceIntegration/src/static/listaIds.txt", mode= "w", encoding="utf-8") as my_file:
        my_file.write(json.dumps(p))
    
if __name__ == '__main__':
    runInit()

"""
 _____ _______ ______ __    _____ ____    _______ _____ 
 |_   _|__   __|  ____| |    / ____/ __ \  |__   __|_   _|
   | |    | |  | |__  | |   | |   | |  | |    | |    | |  
   | |    | |  |  __| | |   | |   | |  | |    | |    | |  
  _| |_   | |  | |____| |___| |___| |__| |    | |   _| |_ 
 |_____|  |_|  |______|______\_____\____/     |_|  |_____|
    
"""
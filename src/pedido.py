from logger import Logger
import requests
import json
import codecs
from src.authentication import Authentication
from MPS.product import Product as MPSProduct

class Pedido():
    """ Clase encargada de realizar pedidos a MPS
    """
    def __init__(self):
        self.url = 'https://shopcommerce.mps.com.co:8081/api/WebApi/RealizarPedido'
        self.payload = {}
        self.headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }
        self.apiWoo = Authentication.generateAPIWoo()
        self.accessTokenMPS = Authentication.getAccessTokenMPS()
        self.accessTokenWoo = Authentication.getAccessTokenWoo()
        self.mpsProductManager = MPSProduct()
        self.pedidoMPS = {
           "listaPedido":[
               {
                    "AccountNum":83040420,
                    "NombreClienteEntrega":"",
                    "ClienteEntrega":"",
                    "TelefonoEntrega":"",
                    "DireccionEntrega":"",
                    "Observaciones": "",
                    "StateId":"0",
                    "CountyId":"0",
                    "RecogerEnSitio":0,
                    "EntregaUsuarioFinal":1,
                    "listaPedidoDetalle":[
                        {
                             "PartNum":"",
                             "Producto":"",
                             "Precio":"",
                             "Cantidad":0,
                             "Marks":"MICROSOFT ESD",
                             "Bodega":"BCOTA"
                         }
                    ]
               }
           ]
        }

    def retrieveMetaOrders(self):
        urlMeta = "https://www.tiendaitelco.com/wc-api/v3/orders?filter[meta]=true"

        header = {
            'Authorization': self.accessTokenWoo
        }
        try:
            metaOrders = requests.get(urlMeta,headers=header).json()
        except:
            print("No se pudo traer meta orders")
        else:
            print("Si se pudo traer meta orders")
            print(metaOrders)

    def findStateCountyId(self, county, state):
        """ El metodo busca los ids del estado 
            y county en archivo y los retorna

        Args:
            county (String): String con el nombre del county {Ciudad}
            state (String): String con el nombre del state {Departamento}

        Returns:
            tuple: Una tupla del countyId y stateId respectivamente
        """
        s = open("/Users/user/OneDrive - Universidad de los Andes/Tienda Itelco/MpsWoocommerceIntegration/src/static/cyd.txt").read()
        decodedData = codecs.decode(s.encode(), 'utf-8-sig')
        cyd = json.loads(decodedData)
        departamentos = cyd['Departamento']
        ciudades = cyd['Cuidades']
        stateId = -1
        countyId = -1
        for dep in departamentos:
            if dep['Name'] == state:
                stateId = dep['StateId']

        for ciudad in ciudades:
            if ciudad['Name'].lower() == county.lower() and ciudad['StateId'] ==  stateId:
                countyId = ciudad['CountyId']

        return countyId,stateId

        

    def retrieveOrders(self):
        url = "https://www.tiendaitelco.com/wc-api/v3/orders?filter[limit]=-1"
        headers = {
            'Authorization': self.accessTokenWoo
        }

        try:
            req = requests.get(url, headers=headers).json()
        except:
            print("Couldn't retrieve orders")
        else:
            print("Retrieved orders")

        return (req)

    def realizarPedido(self, pedidoMPS, orderIds):
        """ Genera el pedido en Woocmerce

        Args:
            productsDetail (Array[Dict]): Es una lista de diccionarios con la información del los productos
            orderDetail (Dict): Es un diccionario con los detalles del pedido
            orderIds (Array[int]): Son los ids de los pedido de Woocommerce
        """
        logger = Logger(True)
        pedido = {"listaPedido":pedidoMPS}
        pedido = json.dumps(pedido)
        print(pedido)
        
        response = requests.request("POST", self.url, headers=self.headers, data=pedido).json()
        if response['Valor'] == 'FAIL':
            print('El pedido {id} no se pudo crear')
            logger.log_error(f'El pedido {id} no se pudo crear')
            logger.log_warning(json.dumps(response))
            logger.log_info("------------ Pedido ------------")
            logger.log_info(pedido)
        else:
            print(f'El pedido {id} se creo exitosamente')
            logger.log_success(f'El pedido {id} se creo exitosamente - [{response["Pedido"]}]')
            logger.log_info("------------ Pedido ------------")
            logger.log_info(pedido)

    def runPedido(self):
        """ Corre todo el archivo de pedido
            Este se esta corriendo cada 30 minutos
        """
        orders = self.retrieveOrders()
        ordersMps = []
        orderIds = []
        
        productosCompletos = True
        count = 0
        for order in orders['orders']:
            productosCompletos = True
            # Pedido que ya quedo pago
            if order['status'] == 'processing':
                #print(count)
                #print(order)
                orderDetail = {}
                productDetail = []
                orderIds.append(order['order_number'])
                orderDetail["AccountNum"] = 83040420
                orderDetail["NombreClienteEntrega"] = order['billing_address']['first_name']+" "+ order['billing_address']['last_name']
                orderDetail["ClienteEntrega"] = "1032497700"
                orderDetail["TelefonoEntrega"] = order['billing_address']['phone']
                orderDetail["DireccionEntrega"] = order['shipping_address']['address_1']
                orderDetail["Observaciones"] = ""
                stateName = order['shipping_address']['state']
                countyName = order['shipping_address']['city']
                countyId,stateId = self.findStateCountyId(countyName,stateName)
                orderDetail["StateId"] = stateId
                orderDetail["CountyId"] = countyId
                orderDetail["RecogerEnSitio"] = 0
                orderDetail["EntregaUsuarioFinal"] = 1
            
                for productInOrder in order['line_items']:
                    p = self.mpsProductManager.getProductBySku(productInOrder['sku'])
                    if p == 0:
                        # Ya no hay inventario del producto - Se deberia notificar de alguna forma
                        print(f'Producto no se encontro {productInOrder["sku"]}')
                        productosCompletos = False
                        logger = Logger(False)
                        logger.log_error(f"Producto {productInOrder['sku']} sin inventario por eso no se realizo el pedido {order['order_number']}")
                    else:
                        product = {}
                        product['PartNum'] = productInOrder['sku']
                        product['Producto'] = productInOrder['name']
                        product['Precio'] = p['precio']
                        product['Cantidad'] = productInOrder['quantity']
                        product['Marks'] = p['Marks']
                        product['Bodega'] = "BCOTA"
                        productDetail.append(product)
                

                if productosCompletos:
                    orderDetail['listaPedidoDetalle'] = productDetail
                count+=1
            ordersMps.append(orderDetail)

        print(ordersMps)
        #self.realizarPedido(ordersMps,orderIds)
            



            
        

if __name__ == '__main__':
    orderManager =  Pedido()
    orderManager.runPedido()     
    #orderManager.retrieveOrders()
    #orderManager.retrieveMetaOrders()
    
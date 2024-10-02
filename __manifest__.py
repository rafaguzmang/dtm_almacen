        #Views
{
    "name":"Almacén",

    'version': '1.0',
    'author': "Rafael Guzmán",
    "description": "Modulo para interactuar con el inventario del almacén",
    "depends":['base',"dtm_diseno"],
    "data":[
        #Security
        'security/ir.model.access.csv',

        #Views
        'views/dtm_almacen_view.xml',
        'views/dtm_almacen_nombres_view.xml',

        #Styles


        #Menú

    ],
    'license': 'LGPL-3',
    'assets': {
    'web.assets_backend': [
        'dtm_almacen/static/src/css/styles.css',
    ],
},
}


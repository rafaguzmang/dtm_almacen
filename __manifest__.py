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
        'views/dtm_almacen_owl_view.xml',
        'views/dtm_almacen_salidas_view.xml',
        #Menú
        'views/dtm_almacen_menu.xml'

    ],
    'license': 'LGPL-3',
    'assets': {
    'web.assets_backend': [
        'dtm_almacen/static/src/css/styles.css',
        'dtm_almacen/static/src/xml/revision.xml',
        'dtm_almacen/static/src/js/revision.js',
        'dtm_almacen/static/src/js/transito.js',
        'dtm_almacen/static/src/xml/transito.xml',
        'dtm_almacen/static/src/js/salidas.js',
        'dtm_almacen/static/src/xml/salidas.xml',
        ],
    },
}

from odoo import http
from odoo.http import request
import datetime
import json

class Material(http.Controller):
    # Se obtiene el total del material indirecto requerido por las ordenes GET
    @http.route('/revision_material', type='http',auth='public',csrf=False)
    def indirecto(self):
        # Se obtiene la lista de los materiales que deben ser revisados por almacen
        get_materials_line = request.env['dtm.materials.line'].sudo().search([('almacen','!=',True),('materials_cuantity','>',0),('model_id','!=',False)])
        get_norepetidos = list(set(get_materials_line.mapped('materials_list.id')))
        resultado = []
        # Se itera por el resultado de los codigos que deben ser revisados y que no estan repetidos
        for codigo in get_norepetidos:
            # Se obtienen todas las ordenes que requieren este material
            get_materiales = request.env['dtm.materials.line'].search([('materials_list','=',codigo)])
            # Se filtra el material no revisado por almacén
            get_materiales_filtros = get_materiales.filtered(lambda r:r.materials_cuantity >= r.materials_availabe and r.materials_required > 0 and not r.almacen  and r.model_id.firma_ventas)
            if get_materiales_filtros:
                # Se filtra para obtener el apartado tomando en cuenta los items que no se han estregado
                get_apartado = get_materiales.filtered(lambda r: r.materials_required > 0  and r.model_id.firma_ventas)
                # Se obtienen los datos del material del almacén
                stock = get_materiales[0].materials_list.cantidad
                apartado = sum(get_apartado.mapped('materials_cuantity'))
                nombre = get_materiales[0].materials_list.nombre
                medida = get_materiales[0].materials_list.medida
                cantidad = sum(get_materiales_filtros.mapped('materials_cuantity'))
                # entregado = sum(get_materiales_filtros.mapped('materials_availabe'))
                get_requerido = request.env['dtm.compras.requerido'].sudo().search([('codigo','=',codigo),('nombre','=',f"{nombre} {medida}")])
                get_realizado = request.env['dtm.compras.realizado'].sudo().search([('codigo','=',codigo),('nombre','=',f"{nombre} {medida}"),('comprado','not in',["Recibido","Parcial"])])
                en_compras = sum(get_realizado.mapped('cantidad')) + sum(get_requerido.mapped('cantidad'))
                comprar = max(apartado - en_compras - stock,0)
                if stock >= apartado:
                    comprar = 0;

                if cantidad > 0:
                    resultado.append({
                            'codigo':codigo,
                            'descripcion': f"{nombre} {medida}",
                            'stock': stock,
                            'apartado':apartado,
                            'requerido':cantidad,
                            'en_compras':en_compras,
                            'comprar':comprar,
                    })
        return request.make_response(
            json.dumps(resultado),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        )
        # return list_result
    # Recibe la confirmación del material para ser comprado en caso de que no haya en existencia POST
    @http.route('/material_compras', type='json', auth='public', csrf=False)
    def compras(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = data.get('codigo')
        nombre = data.get('descripcion')
        lamina_list = ["120.0 x 48.0", "96.0 x 48.0", "96.0 x 36.0", "60.0 x 48.0", ",236.0", "120.0 x 72.0"]
        perfileria_list  = ["Perfil", "Tubo", "P.T.R.","Ángulos","Canales","I.P.R","Varilla","Viga"]
        permiso = True
        if 'Lámina' in nombre:
            permiso = True in [medida in nombre for medida in lamina_list]

        if True in [perfileria in nombre for perfileria in perfileria_list]:
            permiso = "236.0" in nombre
        # Se buscan la ordenes que ya está en cotización para restarlo de las nuevas solicitudes y no mutar en la cantidad
        get_cotizacion = request.env['dtm.compras.requerido'].sudo().search([('codigo','=',codigo),('nombre','=',nombre)])
        # cantidad_cotizacion = sum(get_cotizacion.mapped('cantidad'))
        #Busca si el material ya esta en compras ya sea para comprar o en espera, mas no recibido
        get_compras = request.env['dtm.compras.realizado'].sudo().search([('codigo','=',codigo),('nombre','=',nombre),('comprado','!=','Recibido')])
        # cantidad_compras = sum(get_compras.mapped('cantidad'))
        # en_compras = cantidad_compras + cantidad_cotizacion
        comprar = max(data.get('comprar'),0) # Cantidad a comprar

        # Se buscan las ordenes que no están en compras
        list_compras = get_cotizacion.mapped('orden_trabajo') # Se obtienen las ordenes de compras realizado (cotización)
        list_realizado = get_compras.mapped('orden_trabajo') # Se obtienen las ordenes que ya se compraron
        ordenes_compras = list_compras + list_realizado # La lista solo tiene cadena de caracteres
        ordenes_compras = list(set(list(map(int,ordenes_compras)))) # Lista en ints, se quitan repetidos en caso de que hayan
        get_materials_list = request.env['dtm.materials.line'].sudo().search([
            ('materials_list','=',data.get('codigo')),
            ('model_id','!=',False),
            ('materials_cuantity','>',0),
            ])
        # Se buscan las ordenes que estan solicitando el material
        get_materials_list_filtro = get_materials_list.filtered(lambda r: r.materials_cuantity >= r.materials_availabe)# Se filtra por cantidad mayor a material entregado
        lista_materiales = list(set(get_materials_list_filtro.mapped('model_id.ot_number'))) # Se hace un set
        ordenes_faltantes_lts = list(filter(lambda x: x not in ordenes_compras,lista_materiales))#Se obtienen las ordenes que no están en compras
        # Se agregan las odenes a requerido para el control de solicitudes
        for orden in ordenes_faltantes_lts:
            orden_id = request.env['dtm.odt'].sudo().search([('ot_number','=',orden)])# Se obtiene el id de la orden para filtrar
            record = request.env['dtm.materials.line'].sudo().search([('model_id','=',orden_id.id),('materials_list','=',data.get('codigo'))])# Con el id de la orden y el código podemos obtener el item requerido
            get_compras = request.env['dtm.compras.requerido'].sudo().search([('orden_trabajo','=',orden),('tipo_orden','in',['OT','NPI']),('codigo','=',data.get('codigo'))])
            cantidad = record.materials_cuantity if comprar >= record.materials_cuantity else comprar
            # comprar = max(comprar - record.materials_cuantity,0)
            if cantidad > 0 and permiso:
                vals = {
                    'orden_trabajo':orden,
                    'tipo_orden':orden_id.tipe_order,
                    'revision_ot':orden_id.revision_ot,
                    'codigo':data.get('codigo'),
                    'nombre':f"{record.materials_list.nombre} {record.materials_list.medida if record.materials_list.medida else '.' }",
                    'cantidad':cantidad,
                    'disenador':orden_id.disenador,
                    'nesteo': True if orden_id.firma_ingenieria else False,
                }
                get_compras.write(vals) if get_compras else get_compras.create(vals)
            record.almacen = True

        return data
    #-----------------------------------Transito-------------------------------------------
    # Función para el recibo de material
    @http.route('/material_transito', type='http', auth='public', csrf=False)
    def transito(self):
        get_transito = request.env['dtm.compras.realizado'].sudo().search([('listo_btn','=','True'),('comprado','!=','Recibido')])
        list_set = list(set(get_transito.mapped('codigo')))
        result = []
        for codigo in list_set:
            get_transito = request.env['dtm.compras.realizado'].sudo().search([('codigo','=',codigo),('listo_btn','=','True'),('comprado','!=','Recibido')])
            # print(get_transito.mapped('proveedor'),len(list(set(get_transito.mapped('proveedor')))))
            # Se hace el cálculo cuando la cotización es con un mismo proveedor
            if len(list(set(get_transito.mapped('proveedor')))) == 1 and len(list(set([str(c)for c in get_transito.mapped('fecha_compra')]))) ==1 and len(list(set([str(c)for c in get_transito.mapped('orden_compra')]))) ==1:
                # print(sum(get_transito.mapped('cantidad_almacen')))
                vals = {
                    'proveedor':get_transito[0].proveedor,
                    'orden_compra':get_transito[0].orden_compra,
                    'codigo':get_transito[0].codigo,
                    'descripcion':get_transito[0].nombre,
                    'fecha':get_transito[0].fecha_recepcion,
                    'fecha_creacion':get_transito[0].create_date.strftime('%Y-%m-%d'),
                    'solicitado':sum(get_transito.mapped('cantidad')),
                    'recibido':max(sum(get_transito.mapped('cantidad_almacen')),0),
                    'factura':get_transito[0].factura if get_transito[0].factura else '',
                    'notas':get_transito[0].notas_almacen if get_transito[0].notas_almacen else ''
                }
                result.append(vals)
            # El cálculo se hace cuando hay vario proveedores
            else:
                for orden_compra in list(set(get_transito.mapped('orden_compra'))):
                    data = get_transito.filtered_domain([('orden_compra','=',orden_compra)])
                    vals = {
                        'proveedor': data[0].proveedor,
                        'orden_compra':data[0].orden_compra,
                        'codigo': data[0].codigo,
                        'descripcion': data[0].nombre,
                        'fecha': data[0].fecha_recepcion,
                        'fecha_creacion': data[0].create_date.strftime('%Y-%m-%d'),
                        'solicitado': sum(data.mapped('cantidad')),
                        'recibido': max(data[0].cantidad_almacen,0),
                        'factura': data[0].factura,
                        'notas': data[0].notas_almacen
                    }
                    result.append(vals)
        return request.make_response(
            json.dumps(result),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        )

    # Función para capturar cantidad recibida, número de factura y notas ingresadas por almacen Post
    @http.route('/transito_lectura', type='json', auth='public', csrf=False)
    def transitoLectura(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        # Se obtienen lo valores del json
        codigo = data.get('codigo')
        proveedor = data.get('proveedor')
        descripcion = data.get('descripcion')
        cantidad = int(data.get('cantidad'))
        orden_compra = data.get('orden_compra')
        factura = data.get('factura')
        # Se buscan todas las ordenes que se hayan comprado con el mismo proveedor y código
        get_comprado = request.env['dtm.compras.realizado'].sudo().search([
            ('comprado','!=','Recibido'),
            ('codigo','=',codigo),
            ('proveedor','=',proveedor),
            ('nombre','=',descripcion),
            ('orden_compra','=',orden_compra),
            ('orden_compra','=',orden_compra),
            ('listo_btn', '=', 'True'),
        ])
        # Reparte la cantidad ingresada en los diferentes posibles ordenes (diseño)
        for orden in get_comprado:
            # Se obtiene el número de orden
            get_odt = request.env['dtm.odt'].search(
                [('ot_number', '=', orden.orden_trabajo), ('revision_ot', '=', orden.revision_ot)], limit=1)
            # Se obtiene el item relacionado con la orden
            get_item =  get_odt.materials_ids.filtered_domain([('materials_list', '=', codigo)])
            if cantidad > orden.cantidad:# Si la cantidad cubre lo solicitado se iguala lo pedido a lo entregado
                orden.write({'cantidad_almacen':orden.cantidad})
                get_item.write({'materials_availabe': orden.cantidad,
                                'materials_required': 0
                                })
                cantidad -= orden.cantidad
            else:# Si la cantidad es igual o menor se entrega la cantidad y se detiene la iteración
                orden.write({'cantidad_almacen':orden.cantidad_almacen + cantidad})
                get_item.write({'materials_availabe':get_item.materials_availabe + cantidad,
                                'materials_required': get_item.materials_required - cantidad
                                })
                break

        if get_comprado[0].tipo_orden in ['OT','NPI']:
            get_indirecto = request.env['dtm.materiales'].sudo().browse(codigo)
            get_indirecto.write({'cantidad':max(get_indirecto.cantidad + int(data.get('cantidad')),0)})

        if get_comprado[0].tipo_orden in ['Requi']:
            get_directo = request.env['dtm.consumibles'].sudo().search([('id','=',codigo)])
            if get_directo:
                get_directo.write({'cantidad':get_directo.cantidad + int(data.get('cantidad'))})
            else:
                get_herramientas = request.env['dtm.herramientas'].sudo().search([('nombre','=',descripcion)])
                if get_herramientas:
                    get_herramientas.write({'cantidad':max(get_herramientas.cantidad + int(cantidad),0)})
        # Se revisa si la cantidad ingresada por almacén es igual a la cantidad comprada para darlo como recibido total
        get_comprado = request.env['dtm.compras.realizado'].sudo().search([
            ('comprado', '!=', 'Recibido'),
            ('codigo', '=', codigo),
            ('proveedor', '=', proveedor),
            ('nombre', '=', descripcion),
            ('orden_compra', '=', orden_compra),
            ('listo_btn', '=', 'True'),
        ])
        ingresado = sum(get_comprado.mapped('cantidad_almacen'))
        total = sum(get_comprado.mapped('cantidad'))

        vals = {
            "cantidad":int(data.get('cantidad')),
            "cantidad_real":sum(get_comprado.mapped('cantidad_almacen')),
            "proveedor":proveedor,
            "codigo":codigo,
            "descripcion":descripcion,
            "fecha_real":datetime.datetime.now(),
            "factura":factura,
            "notas":data.get('notas')
        }
        request.env['dtm.control.recibido'].sudo().create(vals)
        if ingresado == total:
            # print('Recibido')
            get_comprado.write({'comprado':'Recibido'})
        
        return data

    # Función para capturar número de factura ingresadas por almacen Post
    @http.route('/transito_factura', type='json', auth='public', csrf=False)
    def transitoFactura(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        get_comprado = request.env['dtm.compras.realizado'].sudo().search([('orden_compra','=',data.get('orden_compra')),('codigo','=',data.get('codigo')),('proveedor','=',data.get('proveedor')),('nombre','=',data.get('descripcion'))])
        get_comprado.write({'factura':data.get('factura')})
        return data
    
    # Función para capturar notas ingresadas por almacen Post
    @http.route('/transito_notas', type='json', auth='public', csrf=False)
    def notas(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        get_comprado = request.env['dtm.compras.realizado'].sudo().search([('codigo','=',data.get('codigo')),('proveedor','=',data.get('proveedor')),('nombre','=',data.get('descripcion'))])
        get_comprado.write({'notas_almacen':data.get('notas')})
        return data

    #-----------------------------Material Indirecto---------------------
    # Función para la entrega del material indirecto
    @http.route('/leer_material', type='http', auth='public', csrf=False)
    def inventario(self):
        get_materiales = request.env['dtm.materiales'].sudo().search([])
        result = []
        for material in get_materiales:
            get_materials_list = request.env['dtm.materials.line'].sudo().search([('materials_list','=',material.id),('model_id','!=',False)])
            diferentes = get_materials_list.filtered(lambda record: record.materials_cuantity > record.materials_availabe and record.materials_cuantity > 0)
            apartado = sum([record.materials_cuantity - record.materials_availabe for record in diferentes])
            result.append(
                {
                    'codigo': material.id,
                    'nombre': material.nombre,
                    'medida': material.medida,
                    'cantidad': max(material.cantidad, 0),
                    'apartado': max(apartado, 0),
                    'localizacion': material.localizacion if material.localizacion else '',
                }
            )

        return request.make_response(
            json.dumps(result),
            headers={
                'Content-Type':'application/json',
                'Access-Control-Allow-Origin':'*',
            }
        )
    
    # Función para obtener la lista del personal GET
    @http.route('/leer_personal', type='http', auth='public', csrf=False)
    def personal(self):
        get_personal = request.env['dtm.hr.empleados'].sudo().search([])
        result = [
            {
                'id': person.id,
                'nombre': person.nombre,
            }
            for person in get_personal
        ]

        return request.make_response(
            json.dumps(result),
            headers={
                'Content-Type':'application/json',
                'Access-Control-Allow-Origin':'*',
            }
        )

    # Función para registrar la salida de material POST
    @http.route('/salida_material', type='json', auth='public', csrf=False)
    def salida_material(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = int(data.get('codigo'))
        cantidad_salida = int(data.get('cantidad'))
        responsable = data.get('responsable')

        # Se actualiza el material en almacen
        get_material = request.env['dtm.materiales'].sudo().browse(codigo)
        get_material.write({
            'cantidad': max(get_material.cantidad - cantidad_salida, 0),
        })
        request.env['dtm.almacen.salidas'].sudo().create({
            'codigo_material':codigo,
            'nombre': f"{get_material.nombre} {get_material.medida if get_material.medida else '.'}",
            'tipo': 'Indirecto',
            'cantidad_salida':cantidad_salida,
            'responsable':responsable,
            'fecha_salida':datetime.datetime.now(),
        })

        return data

    # Función para modificar el stock POST
    @http.route('/modificar_stock', type='json', auth='public', csrf=False)
    def modificar_stock(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = int(data.get('codigo'))
        nueva_cantidad = int(data.get('cantidad'))

        # Se actualiza el material en almacen
        get_material = request.env['dtm.materiales'].sudo().browse(codigo)
        get_material.write({
            'cantidad': max(nueva_cantidad, 0),
        })
        return data

    # Función para cargar los consumibles
    @http.route('/material_consumibles', type='http', auth='public', csrf=False)
    def material_directo(self):
        consumibles = request.env['dtm.consumibles'].sudo().search([])
        json_list = []
        for material in consumibles:
            vals = {
                'codigo':material.id,
                'nombre':material.nombre,
                'cantidad':material.cantidad,
                'minimo':material.minimo,
                'maximo':material.maximo,
            }
            json_list.append(vals)
        return request.make_response(
            json.dumps(json_list),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        )

    @http.route('/minimo_consumible',type='json',auth='public',csrf=False)
    def minimo_consumible(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        minimo = data.get('minimo')
        codigo = data.get('codigo')
        get_consumibles = request.env['dtm.consumibles'].sudo().search([('id','=',codigo)],limit=1)
        get_consumibles.write({'minimo':int(minimo)}) if get_consumibles else None
        return {'Listo':minimo}

    @http.route('/entregado_consumible', type='json', auth='public',csrf=False)
    def entregado_consumible(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = data.get('codigo')
        nombre = data.get('nombre')
        cantidad = data.get('cantidad')
        recibe = data.get('recibe')
        notas = data.get('notas')
        request.env['dtm.consumibles.historial'].create({
            'codigo':codigo,
            'nombre':nombre,
            'cantidad':cantidad,
            'recibe':recibe,
            'notas':notas,
        })
        get_consumibles = request.env['dtm.consumibles'].sudo().search([('id','=',codigo)],limit=1)
        get_consumibles.write({'cantidad':max(get_consumibles.cantidad - int(cantidad),0)})

        return {'codigo':codigo}

    @http.route('/cantidad_consumible', type='json', auth='public', csrf=False)
    def cantidad_consumible(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        cantidad = data.get('cantidad')
        codigo = data.get('codigo')
        get_consumibles = request.env['dtm.consumibles'].sudo().search([('id','=',codigo)],limit=1)
        get_consumibles.write({'cantidad':int(cantidad)})
        return {'codigo':codigo}

    @http.route('/material_cortado', type='http', auth='public', csrf=False)
    def material_cortado(self):

        result = [
            {
                'lamina':corte.lamina
            }
            for corte in request.env['dtm.control.laminas'].sudo().search([])
        ]

        return request.make_response(
            json.dumps(result),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin':'*'
            }
        )

    # Borra el material del modelo de las láminas cortadas
    @http.route('/borrar_material', type='json', auth='public', csrf=False)
    def borrar_material(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        lamina = data.get('lamina')
        get_control = request.env['dtm.control.laminas'].sudo().search([('lamina','=',lamina)],limit=1)
        get_control.unlink() if get_control else None

        return {'Borrado':'Borrado'}

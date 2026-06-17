from odoo import http
from odoo.http import request
import json

class Ordenes(http.Controller):

    @http.route('/almacen_ordenes_revision', type='http', auth='public', csrf=False)
    def ordenRevision(self):
        ordenes = request.env['dtm.odt'].sudo().search([('materials_ids.almacen', '!=', True)])
        result = []
        for orden in ordenes:

            result.append({
                'id': orden.id,
                'ot': orden.ot_number,
                'cliente': orden.name_client,
                'proyecto': orden.product_name,
                'fecha': orden.fecha_ventas.strftime('%Y-%m-%d') if orden.fecha_ventas else '',
                'tipo_orden': orden.tipe_order if orden.tipe_order else '',
                'materials': [{
                                'codigo': material.materials_list.id,
                                'nombre': f"{material.materials_list.nombre} - {material.materials_list.medida}",
                                'cantidad': material.materials_cuantity,
                                'inventario': material.materials_availabe,
                                'requerido': material.materials_required,
                                'notas': material.notas,
                                'almacen': material.almacen,
                                'id_linea': material.id,
                               }
                              for material in orden.materials_ids]
            })

        return request.make_response(
            json.dumps(result),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        )

    @http.route('/almacen_check', type='json', auth='public')
    def almacen_check(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        id_linea = data.get('id_linea')
        almacen = data.get('almacen')
        get_material = request.env['dtm.materials.line'].sudo().browse(int(id_linea))
        get_material.write({'almacen': not almacen})
        return {'almacen': not almacen}

    @http.route('/almacen_set_cant', type='json', auth='public')
    def almacen_set_cant(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        id_linea = data.get('id_linea')
        cantidad = data.get('almacen')
        get_material = request.env['dtm.materials.line'].sudo().browse(int(id_linea))
        requerido =  get_material.materials_cuantity - int(cantidad)
        get_material.write({'materials_required':requerido,'materials_availabe': cantidad})
        return {'cantidad': cantidad,'requerido': requerido}

    @http.route('/almacen_mandar_comprar', type='json', auth='public')
    def almacen_mandar_comprar(self):
        medidas_validas = ["240.0 x 96.0","120.0 x 48.0", "96.0 x 48.0", "120.0 x 36.0", "96.0 x 36.0", "60.0 x 48.0","12.0 x 12.0"]
        lista_perfil = ["Perfil", "Tubo", "Canal", "Ángulo", "I.P.R", "Solera","Varilla"]
        medida_perfiles = [",236.0"]

        raw = request.httprequest.data
        data = json.loads(raw)
        materiales = data.get('materiales')
        materiales_int = [int(m) for m in materiales]
        get_material = request.env['dtm.materials.line'].sudo().browse(materiales_int)
        for item in get_material:
            if item.materials_required > 0:
                nombre = item.materials_list.nombre
                medida = item.materials_list.medida
                # Descarta maquinados
                if nombre.startswith("Maquinado") or nombre == "Material Sobrante":
                    continue
                # Descarta pedacería
                if nombre.startswith("Lámina") and not any(validas in medida for validas in medidas_validas):
                    continue
                # Descarta perfilería que no mida 6 metros
                if any(perfil in nombre for perfil in lista_perfil) and not any(medida in medida for medida in medida_perfiles):
                    continue
                get_compras = request.env['dtm.compras.requerido'].sudo().search([('orden_trabajo','=',str(item.model_id.ot_number)),('codigo','=',item.materials_list.id)],limit=1)                
                vals = {
                        'orden_trabajo':str(item.model_id.ot_number),
                        'tipo_orden':item.model_id.tipe_order,
                        'revision_ot':item.model_id.revision_ot,
                        'codigo':item.materials_list.id,
                        'nombre':f"{item.materials_list.nombre} {item.materials_list.medida}",
                        'cantidad':item.materials_required,
                        'disenador':item.model_id.disenador,
                        'nesteo':item.model_id.firma_ingenieria,
                    }            
                get_compras.write(vals) if get_compras else get_compras.create(vals)
            
        return {'ok': '200'}

    @http.route('/almacen_ordenes_entrega', type='http', auth='public')
    def almacen_ordenes_entrega(self):
        get_ordenes = request.env['dtm.odt'].sudo().search([
            ('ot_number', '!=', 0),
            ('firma', '!=', False),
            ('firma_ventas', '!=', False),
            ('firma_ingenieria', '!=', False),
        ])
        result = []
        for orden in get_ordenes:
            result.append({
                'id': orden.id,
                'ot': orden.ot_number,
                'cliente': orden.name_client,
                'proyecto': orden.product_name,
                'tipo_orden': orden.tipe_order if orden.tipe_order else '',               
            })
        
        return request.make_response(
            json.dumps(result),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        )

    @http.route('/almacen_material_entrega', type='json', auth='public')
    def almacen_material_entrega(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        orden = data.get('orden')
        get_materiales = request.env['dtm.odt'].sudo().search([ ('ot_number','=',int(orden))],limit=1).materials_ids
        result = []
        for material in get_materiales:
            result.append({
                'id': material.id,
                'codigo': material.materials_list.id,
                'nombre': f"{material.materials_list.nombre} {material.materials_list.medida}",
                'cantidad': material.materials_cuantity,
                'disponible': material.materials_availabe,
                'requerido': material.materials_required,
                'entregado': material.entregado,
                'recibe': material.recibe,
                'cantidad_entregada':material.cant_entregada,
                'factura':material.factura,
            })

        return result
            
    @http.route('/almacen_personal_recibe', type='http', auth='public')
    def almacen_personal_recibe(self):
        get_personal = request.env['dtm.hr.empleados'].sudo().search([])
        result = []
        for personal in get_personal:
            result.append({
                'id': personal.id,
                'nombre': personal.nombre,
            })
        return request.make_response(
            json.dumps({'result': result}),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        )

    @http.route('/almacen_actualizar_orden', type='json', auth='public')
    def almacen_actualizar_orden(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        id = int(data.get('id'))
        cantidad = int(data.get('cantidad'))
        persona = data.get('persona')
        get_material = request.env['dtm.materials.line'].sudo().browse(id)
        get_material.write({'cant_entregada': get_material.cant_entregada + cantidad,'recibe': persona})
        if cantidad >= get_material.materials_cuantity:
            get_material.write({'entregado': True})

        request.env['dtm.almacen.salidas'].sudo().create({
            'codigo_material':get_material.materials_list.id,
            'nombre':f"{get_material.materials_list.nombre} {get_material.materials_list.medida}",
            'tipo':'Indirecto',
            'responsable':persona,
            'cantidad_salida':cantidad,
        })

        return {'cantidad': get_material.cant_entregada,
                'recibio': get_material.recibe,
            }
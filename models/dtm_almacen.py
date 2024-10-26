from odoo import api,fields,models
import re
from odoo.exceptions import ValidationError, AccessError, MissingError,Warning

class Almacen(models.Model):
    _name = "dtm.almacen"
    _description = "Modelo para llevar el control del almacén"

    inventario_id = fields.Many2one("dtm.diseno.almacen")
    id_inventario = fields.Integer(string="Código", readonly = False)
    codigo = fields.Integer(readonly=True)

    nombre_materiales = fields.Many2one("dtm.almacen.nombres", string="Nombre materiales")
    medidas = fields.Char(string="Medidas", readonly = True)
    medidas_back = fields.Char(readonly = False)
    calibre = fields.Selection(string="Calibre", selection = [('10.0',10.0),('11.0',11.0),('12.0',12.0),
                                                                ('14.0',14.0),('16.0',16.0),('18.0',18.0),
                                                                ('20.0',20.0),('22.0',22.0),("0.375", "3/8"), ("0.25", "1/4"), ("0.1875", "3/16"), ("0.3125", "5/16"),
                                                                ("0.5", "1/2"),("0.625", "5/8"), ("0.75", "3/4"), ("1.0", "1")])

    diametros = fields.Selection(string="Diámetros", selection = [("0.125", "1/8"),("0.25", "1/4"),("0.375", "3/8"),("0.5", "1/2"),("0.625", "5/8"),("0.75", "3/4"),
                                                                ("0.875", "7/8"),("1.0", "1"),("1.125", "1 1/8"),("1.25", "1 1/4"),("1.375", "1 3/8"),("1.5", "1 1/2"),
                                                                ("1.625", "1 5/8"),("1.75", "1 3/4"),("1.875", "1 7/8"),("2.0", "2"),("2.125", "2 1/8"),
                                                                ("2.25", "2 1/4"),("2.375", "2 3/8"),("2.5", "2 1/2"),("2.625", "2 5/8"),("2.75", "2 3/4"),
                                                                ("2.875", "2 7/8"),("3.0", "3"),("3.125", "3 1/8"),("3.25", "3 1/4"),("3.375", "3 3/8"),
                                                                ("3.5", "3 1/2"),("3.625", "3 5/8"),("3.75", "3 3/4"),("3.875", "3 7/8"),("4.0", "4")])
    espesor = fields.Selection(string="Espesor", selection = [("0.125", "0.125"), ("0.17", "0.17"), ("0.184", "0.184"), ("0.18", "0.18"),
                                                                ("0.19", "0.19"), ("0.325", "0.325"), ("0.20", "0.20"), ("0.31", "0.31"),
                                                                ("0.44", "0.44"), ("0.22", "0.22"), ("0.30", "0.30"), ("0.49", "0.49"),
                                                                ("0.24", "0.24"), ("0.38", "0.38"), ("0.53", "0.53"), ("0.67", "0.67"),
                                                                ("0.28", "0.28"), ("0.39", "0.39"), ("0.51", "0.51"), ("0.40", "0.40")])
    largo = fields.Float(string="Largo")
    ancho = fields.Float(string="Ancho")
    alto = fields.Float(string="Alto")

    lamina = fields.Boolean(default=False)
    perfil = fields.Boolean(default=False)
    barras = fields.Boolean(default=False)
    tubos = fields.Boolean(default=False)
    placa = fields.Boolean(default=False)
    solera = fields.Boolean(default=False)
    varilla = fields.Boolean(default=False)
    canal = fields.Boolean(default=False)
    angulos = fields.Boolean(default=False)
    viga = fields.Boolean(default=False)

    cantidad = fields.Integer(string="Stock", readonly = False)
    apartado = fields.Integer(string="Proyectado", readonly = False)
    disponible = fields.Integer(string="Disponible", readonly = False)
    cantidad_nueva = fields.Integer(string="Agregar Cantidad")
    apartado_nueva = fields.Integer(string="Agregar Proyectado")
    disponible_nueva = fields.Integer(string="Agregar Disponible")
    codigo_nuevo = fields.Integer(string="Código", readonly = True)


    localizacion = fields.Char(string="Localización")

    def get_view(self, view_id=None, view_type='form', **options):#Carga los items de todos los módulos de Almacén en un solo módulo de diseño
        res = super(Almacen,self).get_view(view_id, view_type,**options)
        get_self = self.env['dtm.almacen'].search([])
        for result in get_self:
            result.inventario_id = None
            result.id_inventario = None
            result.nombre_materiales = None
            result.lamina = False
            result.perfil = False
            result.barras = False
            result.tubos = False
            result.placa = False
            result.solera = False
            result.varilla = False
            result.canal = False
            result.angulos = False
            result.viga = False
            result.medidas = ""
            result.cantidad_nueva = 0
            result.calibre = None
            result.diametros = None
            result.espesor = None
            result.largo = 0
            result.ancho = 0
            result.alto = 0

        return res
    #Botón agregar
    def action_cargar_stock(self):
        if self.nombre_materiales and self.medidas_back:
            #Busca un id disponible (recicla)
            for find_id in range(1,self.env['dtm.diseno.almacen'].search([], order='id desc', limit=1).id+1):
                if not self.env['dtm.diseno.almacen'].search([("id","=",find_id)]):
                    self.env.cr.execute(f"SELECT setval('dtm_diseno_almacen_id_seq', {find_id}, false);")
                    break
            get_inventario = self.env['dtm.diseno.almacen'].search([("nombre","=",self.nombre_materiales.nombre),("medida","=",self.medidas_back)])
            vals = {
                "nombre":self.nombre_materiales.nombre,
                "medida":self.medidas_back,
                "cantidad":self.cantidad_nueva,
                "localizacion":self.localizacion,
            }
            get_inventario.write(vals) if get_inventario else get_inventario.create(vals)
            get_inventario = self.env['dtm.diseno.almacen'].search([("nombre","=",self.nombre_materiales.nombre),("medida","=",self.medidas_back)])
            self.codigo_nuevo = get_inventario.id
            self.medidas = self.medidas_back

            for find_id in range(1,self.env['dtm.diseno.almacen'].search([], order='id desc', limit=1).id+2):
                if not self.env['dtm.diseno.almacen'].search([("id","=",find_id)]):
                    self.env.cr.execute(f"SELECT setval('dtm_diseno_almacen_id_seq', {find_id}, false);")
                    break
        else:
             raise ValidationError("Nombre y Medida deben estar llenos")

    def action_actualizar(self):
        vals = {
            "cantidad":self.cantidad,
            "localizacion":self.localizacion,
            "apartado":self.apartado,
            "disponible":self.disponible,
        }
        if self.id_inventario:
            self.env['dtm.diseno.almacen'].search([("id","=",self.id_inventario)]).write(vals)

    @api.onchange("nombre_materiales","calibre","diametros","espesor","largo","ancho","alto","medidas_back")
    def onchange_materiales(self):
        self.lamina = False
        self.perfil = False
        self.barras = False
        self.tubos = False
        self.placa = False
        self.solera = False
        self.varilla = False
        self.canal = False
        self.angulos = False
        self.viga = False

        if self.nombre_materiales.nombre:

            if self.nombre_materiales.nombre.find("Lámina") != -1:
                self.diametros = None
                self.espesor = None
                self.alto = 0
                self.lamina = True
                self.medidas = f"{self.largo if self.largo else ''} x {self.ancho if self.ancho else ''} @ {self.calibre if self.calibre else ''}"
                self.medidas_back = f"{self.largo if self.largo else ''} x {self.ancho if self.ancho else ''} @ {self.calibre if self.calibre else ''}"
            if self.nombre_materiales.nombre.find("Perfil") != -1:
                self.diametros = None
                self.espesor = None
                self.perfil = True
                self.medidas = f"{self.alto if self.alto else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}, {self.largo if self.largo else 0}"
                self.medidas_back = f"{self.alto if self.alto else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}, {self.largo if self.largo else 0}"
            if self.nombre_materiales.nombre.find("Barra") != -1:
                self.calibre = None
                self.espesor = None
                self.ancho = 0
                self.alto = 0
                self.barras = True
                self.medidas = f"Ø {self.diametros if self.diametros else ''} x {self.largo if self.largo else 0}"
                self.medidas_back = f"Ø {self.diametros if self.diametros else ''} x {self.largo if self.largo else 0}"
            if self.nombre_materiales.nombre.find("Tubo") != -1:
                self.espesor = None
                self.ancho = 0
                self.alto = 0
                self.tubos = True
                self.medidas = f"{self.diametros if self.diametros else ''} x {self.largo if self.largo else 0} @ {self.calibre if self.calibre else ''}"
                self.medidas_back = f"{self.diametros if self.diametros else ''} x {self.largo if self.largo else 0} @ {self.calibre if self.calibre else ''}"
            if self.nombre_materiales.nombre.find("Placa") != -1:
                self.diametros = None
                self.espesor = None
                self.alto = 0
                self.placa = True
                self.medidas = f"{self.largo if self.largo else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}"
                self.medidas_back = f"{self.largo if self.largo else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}"
            if self.nombre_materiales.nombre.find("Solera") != -1:
                self.diametros = None
                self.espesor = None
                self.alto = 0
                self.solera = True
                self.medidas = f"{self.largo if self.largo else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}"
                self.medidas_back = f"{self.largo if self.largo else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}"
            if self.nombre_materiales.nombre.find("Varilla") != -1:
                self.calibre = None
                self.espesor = None
                self.ancho = 0
                self.alto = 0
                self.varilla = True
                self.medidas = f"Ø {self.diametros if self.diametros else ''} x {self.largo if self.largo else 0}"
                self.medidas_back = f"Ø {self.diametros if self.diametros else ''} x {self.largo if self.largo else 0}"
            if self.nombre_materiales.nombre.find("Canal") != -1:
                self.calibre = None
                self.diametros = None
                self.canal = True
                self.medidas = f"{self.alto if self.alto else 0} x {self.ancho if self.ancho else 0} espesor {self.espesor},{self.largo if self.largo else 0}"
                self.medidas_back = f"{self.alto if self.alto else 0} x {self.ancho if self.ancho else 0} espesor {self.espesor},{self.largo if self.largo else 0}"
            if self.nombre_materiales.nombre.find("Ángulo") != -1:
                self.diametros = None
                self.espesor = None
                self.angulos = True
                self.medidas = f"{self.alto if self.alto else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''},{self.largo if self.largo else 0}"
                self.medidas_back = f"{self.alto if self.alto else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''},{self.largo if self.largo else 0}"
            if self.nombre_materiales.nombre.find("Viga") != -1:
                self.diametros = None
                self.espesor = None
                self.alto = 0
                self.viga = True
                self.medidas = f"{self.largo if self.largo else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}"
                self.medidas_back = f"{self.largo if self.largo else 0} x {self.ancho if self.ancho else 0} @ {self.calibre if self.calibre else ''}"

    @api.onchange("inventario_id")
    def onchange_inventario(self):
        self.id_inventario = self.inventario_id.id
        self.codigo = self.inventario_id.id
        self.cantidad = self.inventario_id.cantidad
        self.apartado = self.inventario_id.apartado
        self.disponible = self.inventario_id.disponible
        get_inventario = self.env['dtm.diseno.almacen'].search([]).mapped('nombre')
        list_items = []
        for item in get_inventario:
            if item:
                item = re.sub("[cC][aA][rR][bB][oóO][nN]", "carbón", item)
                item = re.sub("[Ll][aAá][mM][iI][nN][aA]", "Lámina", item)
                item = re.sub("[aA][cC][eE][rR][oO]", "Acero", item)
                item = re.sub("[pP][eE][rR][fF][iI][lL]", "Perfil", item)
                item = re.sub("[Bb][aA][rR][rR][aA]", "Barra", item)
                item = re.sub("[tT][uU][bB][oO]", "Tubo", item)
                item = re.sub("[pP][lL][aA][cC][aA]", "Placa", item)
                item = re.sub("[pP][tT][rR]", "PTR", item)
                item = re.sub("[sS][oO][lL][eE][rR][aA]", "Solera", item)
                item = re.sub("[vV][aA][rR][iI][lL][lL][aA]", "Varilla", item)
                item = re.sub("[cC][aA][nN][aA][lL]", "Canal", item)
                item = re.sub("[aAáÁ][nN][gG][uU][lL][oO]", "Ángulo", item)
                item = re.sub("[vV][iI][gG][aA]", "Viga", item)
                item = re.sub("[mM][aA][qQ][uU][iI][nN][aA][dD][oO][\ssS]", "", item)
                item = re.sub("[pP][oO][lL][iI][cC][aA][rR][bB][oO][nN][aA][tT][oO]", "Policarbonato", item)
                item = re.sub("[uU][nN][iI][cC][aA][nN][aA][lL]", "Unicanal", item)
                item = re.sub("^\s+|\s+$", "", item)
                if re.findall("Lámina|Perfil|Barra|Tubo|Placa|Solera|Varilla|Canal|Ángulo|Viga", item):
                    list_items.append(item)
        list_items = list(set(list_items))
        for nombre in list_items:
            get_nombre = self.env['dtm.almacen.nombres'].search([("nombre","=",nombre)])
            get_nombre.write({'nombre':nombre}) if get_nombre else get_nombre.create({'nombre':nombre})


class Materiales(models.Model):
    _name = "dtm.almacen.nombres"
    _description = "Modelo para almacenar todos los nombres que están dados en el inventario"
    _rec_name = "nombre"

    nombre = fields.Char(string="Material")



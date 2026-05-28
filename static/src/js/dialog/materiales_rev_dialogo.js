/** @odoo-module **/
import { Component, useState } from "@odoo/owl";


export class MaterialesRevDialogo extends Component {
    static props = ['cerrar', 'materiales', 'orden', 'proyecto', 'cliente', 'tipo_orden', 'ordenes']
    setup() {
        this.state = useState({
            materiales: this.props.materiales,
            openConfirmacion: false,
            ultimo: null,
        });
    }

    async mandarComprar() {
        console.log(this.state.materiales);
        const materiales = this.state.materiales.map(m => m.id_linea);
        console.log(materiales);
        const raw = await fetch('/almacen_mandar_comprar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                materiales: materiales,
            }),
        });
        const result = await raw.json();
        console.log(result.result);
        this.state.openConfirmacion = false;
        this.props.ordenes();
        this.props.cerrar();
    }

    confirmarCierre() {
        this.state.materiales.find(m => m.id_linea === this.state.ultimo).almacen = false;
        this.state.openConfirmacion = false;
    }

    async updateStock(id_linea, almacen, cantidad) {
        console.log(almacen, cantidad)
        if (parseInt(almacen) <= parseInt(cantidad)) {
            const response = await fetch('/almacen_set_cant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id_linea: id_linea,
                    almacen: parseInt(almacen),
                }),
            })
            const result = await response.json();
            const new_array = this.state.materiales.map((m) => m.id_linea === id_linea ? { ...m, requerido: result.result.requerido, inventario: result.result.cantidad } : m);
            this.state.materiales = new_array;
        } else {
            alert("Inventario no puede ser mayor a la cantidad solicitada");
        }
    }

    async checkMaterial(id_linea, almacen) {
        this.state.ultimo = id_linea;
        const raw = await fetch('/almacen_check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id_linea: id_linea,
                almacen: almacen,
            }),
        });
        const result = await raw.json();
        this.state.materiales.find((m) => m.id_linea === id_linea).almacen = result.result.almacen;
        console.log("todo revisado", this.state.materiales.every((m) => m.almacen === true));
        this.state.openConfirmacion = this.state.materiales.every((m) => m.almacen === true) ? true : false;
        console.log(this.state.openConfirmacion);
    }


}

MaterialesRevDialogo.template = "dtm_almacen.MaterialesRevDialogo";


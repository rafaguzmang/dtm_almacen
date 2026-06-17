/**@odoo-module**/
import { Component, onWillStart, useState } from "@odoo/owl";

export class EntregasOrdenesDialogo extends Component {
    static props = ["cerrar", "orden", "cliente", "proyecto", "tipo_orden"];

    setup() {
        this.state = useState({
            materiales: [],
            personal: [],
        });
        onWillStart(async () => {
            await this.ordenes();
            await this.personal();
        })
    }

    entregaMaterial = async (ev, id) => {
        const fila = ev.target.closest("tr");
        const persona = this.state.personal.find(p => p.id == parseInt(fila.querySelector("select[name='lista_personal']").value)).nombre;
        const cantidad_ingresada = fila.children[6].children[0].value;
        if (cantidad_ingresada > 0 && persona != "") {
            const response = await fetch('/almacen_actualizar_orden', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id,
                    cantidad: cantidad_ingresada,
                    persona: persona
                }),
            });
            const data = await response.json();
            this.ordenes();
        } else {
            alert("Debe ingresar una cantidad y seleccionar una persona");
        }
    }



    ordenes = async () => {
        const response = await fetch('/almacen_material_entrega', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ orden: this.props.orden }),
        });
        const data = await response.json();
        this.state.materiales = data.result;
    }
    personal = async () => {
        const response = await fetch('/almacen_personal_recibe', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        this.state.personal = data.result;
    }
}

EntregasOrdenesDialogo.template = "dtm_almacen.entregas_ordenes_dialogo";
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Consumibles extends Component {
    setup() {
        this.state = useState({
            consumibles: [],
            empleados: [],
        })

        onWillStart(async () => {
            await this.cargarConsumibles();
            await this.empleados();
        })

    }

    async entregarConsumible(event) {
        const cantidad = event.target.value;
        const codigo = event.target.closest('tr').querySelector('[name=td_codigo]').innerText;
        const nombre = event.target.closest('tr').querySelector('[name=td_nombre]').innerText;
        const select = event.target.closest('tr').querySelector('[name=lista_personal]');
        const recibe = select?.options[select.selectedIndex].text ?? '';
        const notas = event.target.closest('tr').querySelector('[name=notas]').value;
        if (recibe === '--') {
            alert('Seleccione un responsable para la salida de material');
            event.target.value = 0;
            return;
        } else if (cantidad <= 0) {
            alert('Ingrese una cantidad válida para la salida de material');
            return;
        } else {
            const response = await fetch("/entregado_consumible", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    cantidad: cantidad,
                    codigo: codigo,
                    recibe: recibe,
                    notas: notas,
                })
            });
            const data = await response.json();
            console.log(data);
            await this.cargarConsumibles();
            // Limpiar campos después de la entrega exitosa
            event.target.value = "";
            if (select) select.selectedIndex = 0; // Resetear al primer elemento (-- o vacío)
            const notasInput = event.target.closest('tr').querySelector('[name=notas]');
            if (notasInput) notasInput.value = "";
        }
    }

    async minimoConsumible(event) {
        const valor = event.target.value;
        const codigo = event.target.closest('tr').querySelector('[name=td_codigo]').innerText;
        const response = await fetch("/minimo_consumible", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                minimo: valor,
                codigo: codigo,
            })
        });
        const data = await response.json();
        await this.cargarConsumibles();
    }

    async cargarConsumibles() {
        const response = await fetch("/material_consumibles");
        const data = await response.json();
        this.state.consumibles = data;
    }

    async empleados() {
        const response = await fetch("/leer_personal");
        const data = await response.json();
        this.state.empleados = data;
        console.log(this.state.empleados);
    }

}

Consumibles.template = "dtm_almacen.consumibles"
registry.category("actions").add("dtm_almacen.consumibles", Consumibles)

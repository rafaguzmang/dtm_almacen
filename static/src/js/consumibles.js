/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Consumibles extends Component {
    setup() {
        this.state = useState({
            consumibles: [],
            empleados: [],
            filtro_tabla: [],
        })

        onWillStart(async () => {
            await this.cargarConsumibles();
            await this.empleados();
        })

    }

    // Filtros
    async buscarCodigo(event) {
        // Al buscar por código, se invalidan los demás filtros
        const inputs = document.querySelectorAll('input[name^="search_"]');
        inputs.forEach(input => {
            if (input !== event.target) input.value = '';
        });

        const codigo = event.target.value.trim();
        if (codigo === "") {
            // Si está vacío, restaurar todos
            this.state.consumibles = this.state.filtro_tabla;
        } else {
            // Búsqueda exacta
            this.state.consumibles = this.state.filtro_tabla.filter(c => c.codigo == codigo); // Comparación laxa por si tipos difieren, o estricta si seguros. String vs Number.
        }
        console.log("Búsqueda exacta por código:", codigo);
    }

    async cantidadConsumible(event) {
        const cantidad = event.target.value;
        const codigo = event.target.closest('tr').querySelector('[name=td_codigo]').innerText;
        const response = await fetch("/cantidad_consumible", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                cantidad: cantidad,
                codigo: codigo,
            })
        });
        const data = await response.json();
        await this.cargarConsumibles();
    }

    async buscarConsumible(event) {
        // Al buscar por otros campos, se invalida el código
        const inputCodigo = document.querySelector('input[name="search_codigo"]');
        if (inputCodigo) inputCodigo.value = '';
        const nombre = event.target.value;
        console.log(nombre);
        this.state.consumibles = this.state.filtro_tabla.filter(c => c.nombre.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().includes(nombre.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()));

    }

    async entregarConsumible(event) {
        const cantidad = event.target.value;
        const codigo = event.target.closest('tr').querySelector('[name=td_codigo]').innerText;
        const nombre = event.target.closest('tr').querySelector('[name=td_nombre]').innerText;
        const select = event.target.closest('tr').querySelector('[name=lista_personal]');
        const recibe = select?.options[select.selectedIndex].text ?? '';
        const notas = event.target.closest('tr').querySelector('[name=notas]').value;
        if (recibe === 'Seleccionar...') {
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
                    nombre: nombre,
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
        this.state.filtro_tabla = data;
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

/** @odoo-module */

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { EntregasOrdenesDialogo } from "./dialog/meterial_entrega_dialogo";

export class OrdenesEntrega extends Component {
    static components = { EntregasOrdenesDialogo };
    setup() {
        this.state = useState({
            ordenes: [],
            ordenes_main: [],
            materiales: [],
            clientes: [],
            orden: "",
            tipo_orden: "",
            cliente: "",
            proyecto: "",
            entregaMaterialesDialogo: false,
            ordenMaterial: "",
            ordenCliente: "",
            ordenProyecto: "",
            ordenTipoOrden: "",
            nombreMaterial: "",
            medidaMaterial: "",
        });

        onMounted(async () => {
            await this.ordenes();
        })
    }

    async codigoMaterialFiltro(ev) {
        const codigo = ev.target.value;
        const fila = ev.target.closest('tr');

        // Limpia nombre y medida (input visual + estado)
        fila.children[1].children[0].value = "";
        fila.children[2].children[0].value = "";
        this.state.nombreMaterial = "";
        this.state.medidaMaterial = "";

        if (codigo === "") {
            this.state.ordenes = this.state.ordenes_main;
            return;
        }

        try {
            const response = await fetch('/almacen_codigo_material_filtro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codigo })
            });
            const data = await response.json();
            const resultado = data.result;

            const ordenesFiltradas = this.state.ordenes_main.filter(o =>
                resultado.some(item => String(item.orden) === String(o.ot))
            );

            this.state.ordenes = ordenesFiltradas.map(o => {
                const info = resultado.find(item => String(item.orden) === String(o.ot));
                return { ...o, completo: info.completo, entregado: info.entregado };
            });
        } catch (error) {
            console.error("Error en codigoMaterialFiltro:", error);
        }
    }

    async nombreMaterialFiltro(ev) {
        this._limpiarCodigoMaterial(ev);
        this.state.nombreMaterial = ev.target.value;
        await this._filtrarPorNombreYMedida();
    }

    async medidaMaterialFiltro(ev) {
        this._limpiarCodigoMaterial(ev);
        this.state.medidaMaterial = ev.target.value;
        await this._filtrarPorNombreYMedida();
    }

    _limpiarCodigoMaterial(ev) {
        const fila = ev.target.closest('tr');
        const codigoInput = fila.children[0].children[0];
        codigoInput.value = "";
    }

    async _filtrarPorNombreYMedida() {
        const nombre = this.state.nombreMaterial;
        const medida = this.state.medidaMaterial;

        if (nombre === "" && medida === "") {
            this.state.ordenes = this.state.ordenes_main;
            return;
        }

        try {
            const response = await fetch('/almacen_nombre_material_filtro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, medida })
            });
            const data = await response.json();
            const resultado = data.result;

            const ordenesFiltradas = this.state.ordenes_main.filter(o =>
                resultado.some(item => String(item.orden) === String(o.ot))
            );

            this.state.ordenes = ordenesFiltradas.map(o => {
                const info = resultado.find(item => String(item.orden) === String(o.ot));
                return { ...o, completo: info.completo, entregado: info.entregado };
            });
        } catch (error) {
            console.error("Error en _filtrarPorNombreYMedida:", error);
        }
    }

    verMateriales = (orden, cliente, proyecto, tipo_orden) => {
        this.state.entregaMaterialesDialogo = true;
        this.state.ordenMaterial = orden;
        this.state.ordenCliente = cliente;
        this.state.ordenProyecto = proyecto;
        this.state.ordenTipoOrden = tipo_orden;
    }

    cerrarDialogo = () => {
        this.state.entregaMaterialesDialogo = false;
    }

    proyectoFiltro = (ev) => {
        const fila = ev.target.closest('tr');
        this.state.proyecto = ev.target.value;
        fila.children[0].children[0].value = "";
        this.state.ordenes = ev.target.value != "" ? this.state.ordenes_main.filter(proyecto => proyecto.proyecto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().includes(ev.target.value)) : this.state.ordenes_main;
        this.state.ordenes = this.state.tipo_orden != "" ? this.state.ordenes.filter(tipo => tipo.tipo_orden == this.state.tipo_orden) : this.state.ordenes;
        this.state.ordenes = this.state.cliente != "" ? this.state.ordenes.filter(cliente => cliente.cliente == this.state.cliente) : this.state.ordenes;
        this.state.clientes = [...new Set(this.state.ordenes.filter(o => o.cliente != null).map(item => item.cliente))];
    }

    clienteFiltro = (ev) => {
        const fila = ev.target.closest('tr');
        this.state.cliente = ev.target.value;
        fila.children[0].children[0].value = "";
        this.state.ordenes = ev.target.value != "" ? this.state.ordenes_main.filter(cliente => cliente.cliente == ev.target.value) : this.state.ordenes_main;
        this.state.ordenes = this.state.tipo_orden != "" ? this.state.ordenes.filter(tipo => tipo.tipo_orden == this.state.tipo_orden) : this.state.ordenes;
        this.state.ordenes = this.state.proyecto != "" ? this.state.ordenes.filter(proyecto => proyecto.proyecto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().includes(this.state.proyecto)) : this.state.ordenes;
        this.state.clientes = [...new Set(this.state.ordenes.filter(o => o.cliente != null).map(item => item.cliente))];


    }

    tipoOrdenFiltro = (ev) => {
        const fila = ev.target.closest('tr');
        this.state.tipo_orden = ev.target.value;
        fila.children[0].children[0].value = "";
        this.state.ordenes = ev.target.value != "" ? this.state.ordenes_main.filter(tipo => tipo.tipo_orden == ev.target.value) : this.state.ordenes_main;
        this.state.ordenes = this.state.cliente != "" ? this.state.ordenes.filter(cliente => cliente.cliente == this.state.cliente) : this.state.ordenes;
        this.state.ordenes = this.state.proyecto != "" ? this.state.ordenes.filter(proyecto => proyecto.proyecto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().includes(this.state.proyecto)) : this.state.ordenes;
        this.state.clientes = [...new Set(this.state.ordenes.filter(o => o.cliente != null).map(item => item.cliente))];

    }

    codigoFiltro = (ev) => {
        const fila = ev.target.closest('tr');
        fila.children[1].children[0].value = "";
        fila.children[2].children[0].value = "";
        fila.children[3].children[0].value = "";
        this.state.ordenes = ev.target.value != "" ? this.state.ordenes_main.filter(o => o.ot == ev.target.value) : this.state.ordenes_main;
    }



    ordenes = async () => {
        const response = await fetch('/almacen_ordenes_entrega', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const data = await response.json();
        this.state.clientes = [...new Set(data.filter(o => o.cliente != null).map(item => item.cliente))];
        this.state.ordenes = data.sort((a, b) => parseInt(a.id) - parseInt(b.id));
        this.state.ordenes_main = this.state.ordenes;
    }

}

OrdenesEntrega.template = "dtm_almacen.orden_entrega";
registry.category("actions").add("dtm_almacen.orden_entrega", OrdenesEntrega);
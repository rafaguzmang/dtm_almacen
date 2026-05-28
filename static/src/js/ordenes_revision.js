/** @odoo-module **/
import { Component, useState, onMounted, onWillStart, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { MaterialesRevDialogo } from "./dialog/materiales_rev_dialogo";
import { useService } from "@web/core/utils/hooks";

export class OrdenesDialogo extends Component {
    static components = { MaterialesRevDialogo };
    setup() {
        this.state = useState({
            ordenes: [],
            dialogoAbierto: false,
            materiales: [],
            orden: "",
            proyecto: "",
            cliente: "",
            tipo_orden: "",
        });
        this.busService = useService("bus_service");
        this.onBusNotification = this.onBusNotification.bind(this)

        onMounted(async () => {
            await this.ordenes();

            // this.busService.addChannel('canal_diseno');
            // this.busService.addEventListener('notification', this.onBusNotification);
        })
        onWillStart(async () => {
            this.busService.addChannel('canal_diseno');
            this.busService.addEventListener('notification', this.onBusNotification);
        })
        onWillUnmount(() => {
            this.busService.removeEventListener('notification', this.onBusNotification);
        })
    }

    onBusNotification(notifications) {
        console.log("Paquete recibido del bus", notifications);
        this.ordenes();
    }

    materialesDialogo(materiales, orden, proyecto, cliente, tipo_orden) {
        this.state.dialogoAbierto = true;
        this.state.materiales = materiales;
        this.state.orden = orden;
        this.state.proyecto = proyecto;
        this.state.cliente = cliente;
        this.state.tipo_orden = tipo_orden;
    }

    cerrar = () => {
        this.state.dialogoAbierto = false;
    }

    ordenes = async () => {
        const response = await fetch('/almacen_ordenes_revision', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const data = await response.json();
        const ordenes = data.map(orden => ({ total: orden.materials.length, ...orden }));
        this.state.ordenes = ordenes.sort((a, b) => parseInt(a.ot) - parseInt(b.ot));
    }


}

OrdenesDialogo.template = "dtm_almacen.orden_revision";
registry.category("actions").add("dtm_almacen.orden_revision", OrdenesDialogo);

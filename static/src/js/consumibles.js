/** @odoo-module **/

import { Component , useState, onWillStart, onMounted,onWillUnmount} from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Consumibles extends Component{
    setup(){
        this.state = useState({
            consumibles:[],
            empleados:[],
        })

        onWillStart(async () => {
            await this.cargarConsumibles();
            await this.empleados();
        })

    }

    async cargarConsumibles(){
        const response = await fetch("/material_consumibles");
        const data = await response.json();
        this.state.consumibles = data;
    }

    async empleados(){
        const response = await fetch("/leer_personal");
        const data = await response.json();
        this.state.empleados = data;
        console.log(this.state.empleados); 
    }

}

Consumibles.template = "dtm_almacen.consumibles"
registry.category("actions").add("dtm_almacen.consumibles",Consumibles)

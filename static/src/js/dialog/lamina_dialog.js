/**@odoo-module **/
import { Component, useState,onWillStart } from "@odoo/owl";

export class LaminaDialogo extends Component{
    static props = ["cerrar"];
    setup(){
        this.state = useState({
            laminas: [],
        });
        this.quitarLamina = this.quitarLamina.bind(this);

        onWillStart(async () => {
            await this.materialCortado();
        });
    }

    async quitarLamina(lamina){
        const response = await fetch('/borrar_material',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({lamina: lamina}),
        });
        const data = await response.json();
        await this.materialCortado();
    }

    async materialCortado(){
        const response = await fetch("material_cortado");
        const data = await response.json();
        let number = 0;
        const record = data.map(row=>({'id':number++,...row}));
        this.state.laminas = record;
    }

}
LaminaDialogo.template = "dtm_almacen.lamina_dialog";

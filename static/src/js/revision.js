/** @odoo-module **/
import { Component, useState,onWillStart,onMounted,onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Revision extends Component{
    setup(){

        this.state = useState({
            materiales:[]
        })
        let interval = null;

        onWillStart(async () => {
            await this.cargarMateriales();
        })

        onMounted(() => {
            interval = setInterval(()=>{
                this.cargarMateriales();
            },50000)
        })

        onWillUnmount(() => {
            clearInterval(interval)
        })
//        Llama a cargar la tabla
        this.cargarMateriales = async () => {
            try {
                  const response = await fetch('/revision_material');
                  const data = await response.json();
                  this.state.materiales = data;
                } catch (error) {
                  console.error("Error al cargar materiales:", error);
                }
            };
    }

//    Botón para validar la información
    async mandarComprar(codigo,descripcion,stock,requerido,comprar) {
        const payload = {   codigo: codigo,
                            descripcion:descripcion,
                            stock:stock,
                            requerido:requerido,
                            comprar:comprar,
                        };
        try {
            const response = await fetch('/material_compras', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            console.log(data.result);
            this.cargarMateriales()

        } catch (error) {
            console.error("Error al enviar JSON:", error);
        }
    }



}

Revision.template = "dtm_almacen.revision"
registry.category("actions").add("dtm_almacen.revision",Revision)

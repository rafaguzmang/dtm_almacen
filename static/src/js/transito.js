/** @odoo-module **/
import { Component, onWillStart, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Transito extends Component{
    setup(){

        this.state = useState({
            entradas:[]
        })
        let interval = null;

        onWillStart(async () => {
            await this.cargarTransito();
        })

        onMounted(() => {
            interval = setInterval(()=>{
               this.cargarTransito();
            },10000)
        })
        onWillUnmount(() => {
            clearInterval(interval)
        })
    }

    async cargarTransito(){
            const response = await fetch("/material_transito");
            const data = await response.json(); 
            let num = 0;
            this.state.entradas = data.map(row => ({num:num++,...row}))
    }
    async cantidadIngresada(ev,proveedor,codigo,descripcion,solicitado,recibido){
        const cantidad = ev.target.value;
        const factura = ev.target.closest('tr').querySelector('[name=factura]').value;
        const notas = ev.target.closest('tr').querySelector('[name=notas]').value;
        const orden_compra = ev.target.closest('tr').querySelector('[name=orden_compra]').innerText;
        console.log(solicitado,recibido,recibido + parseInt(cantidad))
        if((recibido + parseInt(cantidad)) > solicitado){
            alert("La cantidad ingresada supera la cantidad solicitada")
        }
        else{
            try{
                if(factura){
                    const response = await fetch('/transito_lectura',{
                    method:'POST',
                    headers:{
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                            cantidad:cantidad,
                            proveedor:proveedor,
                            orden_compra:orden_compra,
                            codigo:codigo,
                            descripcion:descripcion,
                            solicitado:solicitado,
                            recibido:recibido,
                            factura:factura,
                            notas:notas
                        })
                    })
                }
                else{
                    alert("Es necesario número de Factura.");
                }

                ev.target.value = 0;
                this.cargarTransito();
            }catch (error){
            console.log(error)
        }
        }

    }
    async factura(ev,proveedor,codigo,descripcion,orden_compra){
        clearInterval(this.interval);
        try{
            const response = await fetch('/transito_factura',{
                method:'POST',
                headers:{
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    factura:ev.target.value,
                    orden_compra:orden_compra,
                    proveedor:proveedor,
                    codigo:codigo,
                    descripcion:descripcion,
                })
            })
        }
        catch (error){
            console.log(error)
        }
    }
    async notas(ev,proveedor,codigo,descripcion){
        clearInterval(this.interval);
        try{
            const response = await fetch('/transito_notas',{
                method:'POST',
                headers:{
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    notas:ev.target.value,    
                    proveedor:proveedor,
                    codigo:codigo,
                    descripcion:descripcion,
                })
            })
          

        }
        catch (error){
            console.log(error)
        }
    }

}

Transito.template = "dtm_almacen.transito"
registry.category("actions").add("dtm_almacen.transito", Transito)

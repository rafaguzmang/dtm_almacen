/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Salidas extends Component{
    setup(){
        this.state = useState({
            materiales:[],
            personal:[],
            filtro:[],
        })

        onWillStart(async () => {
            await this.cargarMaterial();
            await this.cargarPersonal();            
        })        
    }
    async cargarMaterial(){
            const response = await fetch("/leer_material");
            const data = await response.json();
            this.state.materiales = data;
            this.state.filtro = data;

            // console.log(this.state.materiales)
    }

    async cargarPersonal(){
        const response = await fetch("/leer_personal");
        const data = await response.json();
        this.state.personal = data;
        // console.log(this.state.personal)
    }

    async cantidadSalida(event){
//      datos pata ingresar cantidad
        const cantidad = event.target.value;
        const codigo = event.target.closest('tr').querySelector('[name=codigo_material]').innerText;
        const select = event.target.closest('tr').querySelector('[name=lista_personal]');
        const responsable = select?.options[select.selectedIndex]?.text ?? '';        
        if(responsable==='--Seleccione--'){
            alert('Seleccione un responsable para la salida de material');
            event.target.value = 0;
            return;
        }else if(cantidad<=0){
            alert('Ingrese una cantidad válida para la salida de material');
            return;         
        }else{  
            const response = await fetch("/salida_material", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    
                },
                body: JSON.stringify(
                    {
                        'cantidad': cantidad,
                        'codigo': codigo,
                        'responsable': responsable,
                    }),           
            });
            const data = await response.json();        
            console.log(data.result);
            this.cargarMaterial();
        }
        
    }

    // Actualizar stock al cambiar el valor en el input
    async actualizarStock(event){
        const cantidad = event.target.value;               
        const codigo = event.target.closest('tr').querySelector('[name=codigo_material]').innerText;
        console.log(cantidad,codigo);
        const response = await fetch("/modificar_stock", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                'cantidad': cantidad,
                'codigo': codigo,
            }), 
        })    
        const data = await response.json();        
        console.log(data.result);  
        this.cargarMaterial();
    }

    // -----------------------------------Funciones de filtro-------------------------
    // Función para filtrar por código
    codigoFiltro(event){
        const codigo = event.target.value;
        // Se borran los otros filtros
            // nombre
        event.target.closest('tr').querySelector('[name=nombre_filtro]').value = '';
            // medida
        event.target.closest('tr').querySelector('[name=medida_filtro]').value = '';
            // stock
        const resultado = this.state.filtro.filter(material => material.codigo === parseInt(codigo));
        this.state.materiales = resultado; 

    }
    // Recibe el filtro de nombre
    nombreFiltro(event){
        // Se borra el filtro de código
        event.target.closest('tr').querySelector('[name=codigo_filtro]').value = '';
        // Se obtiene el valor del filtro de medida        
        const medida = (event.target.closest('tr').querySelector('[name=medida_filtro]').value??'').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // elimina los diacríticos
        const stock = event.target.closest('tr').querySelector('[name=stock_filtro]').value??'';
        const nombre = event.target.value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        this.filtro(nombre, medida, stock);          
    } 
    // Recibe el filtro de medida
    medidaFiltro(event){
        // Se borra el filtro de código
        event.target.closest('tr').querySelector('[name=codigo_filtro]').value = '';
        // Se obtiene el valor del filtro de medida y stock        
        let nombre = (event.target.closest('tr').querySelector('[name=nombre_filtro]').value??'').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");  
        const stock = event.target.closest('tr').querySelector('[name=stock_filtro]').value??'';
        const medida = event.target.value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // elimina los diacríticos
        this.filtro(nombre, medida, stock);
    } 
    // Recibe el filtro de stock
    stockFiltro(event){
        const optionselect = event.target.value;   
        const nombre = (event.target.closest('tr').querySelector('[name=nombre_filtro]').value??'').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");  
        const medida = (event.target.closest('tr').querySelector('[name=medida_filtro]').value??'').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // elimina los diacríticos        
        this.filtro(nombre, medida, optionselect);        
    }
    // Función común para filtrar
    filtro(nombre, medida, stock){
        let resultado = this.state.filtro.filter(material => String(material.nombre || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").includes(nombre));
        resultado = resultado.filter(material => String(material.medida || "").includes(medida));
        if(stock==='sin_stock'){
            resultado = resultado.filter(material => material.cantidad <= 0);
        }else if(stock==='con_stock'){
            resultado = resultado.filter(material => material.cantidad > 0);
        }else{
            resultado = resultado;
        }        
        this.state.materiales = resultado;
        // Restablece los filtros si están vacíos
        if(nombre==='' && medida==='' && stock===''){
            this.state.materiales = this.state.filtro;
        }   
    }
}   

Salidas.template = "dtm_almacen.salidas";

registry.category("actions").add("dtm_almacen.salidas", Salidas);



// Obtenemos los elementos del botón y del contenedor desde el archivo HTML.
const button = document.getElementById("theButton")
const data = document.getElementById("info")

// Creamos un array de coches para enviar al servidor.
/*const cars = [
 { "make":"Porsche", "model":"911S" },
 { "make":"Mercedes-Benz", "model":"220SE" },
 { "make":"Jaguar","model": "Mark VII" }
];*/
const cars = {
    "make":"funciona!!",
    "model":"funciona!!"
}

// Creamos un evento "onclick" para el botón.
button.onclick= function(){

    // Obtenemos el endpoint del receptor desde Python utilizando el método "fetch".
    fetch(
            "http://127.0.0.1:8000/receiver",

            {
                method: 'POST',
                headers: {
                    'Content-type': 'application/json',
                    'Accept': 'application/json'
                },
            
                // Convertimos los datos a enviar en formato JSON.
                body:JSON.stringify(cars)
            }
    ).then(
        res=>{
            if(res.ok){
                // Si la respuesta del servidor es exitosa, convertimos los datos de la respuesta a JSON.
                return res.json()
            }else{
                // Si la respuesta no es exitosa, mostramos una alerta al usuario.
                alert("Algo ha salido mal")
            }
        }
    ).then(
        jsonResponse=>{
            // Mostramos los datos de la respuesta en la consola.
            console.log(jsonResponse)
        }
    ).catch(
        (err) => console.error(err)
    );
            
}
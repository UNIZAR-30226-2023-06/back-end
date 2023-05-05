Chat esta en ./chat, ahora mismo seria otro servicio/servidor
pero se puede anadir al servidor principal

el hostname deberia ser 0.0.0.0 para poder comunicarse con android,
y cambiar el puerto si se quiere ejecutar los dos servicios a la vez

En chat/chat.py hay una pequena demo, dirigete a http://hostname:port/room/<room-name>
para chatear en esa sala.

Ademas de permitir chatear con muchas salas, se puede elegir el numero de mensajes a guardar
en memoria (cola fifo) que es esencial para mi solucion en kotlin(puede que haya mejores).

manager = ConnectionManager(5) # las salas guardaran los 5 ultimos mensajes y al pedir sincronizacion
                               # se reenviaran al que lo ha pedido

 ahora todos los mensajes que envian los clientes lo hacen en 
texto plano y puede que puedan "injectar" jsons, lo cambiare lo antes posible


no puede explicar todo aqui, si no se entiende el codigo decidme
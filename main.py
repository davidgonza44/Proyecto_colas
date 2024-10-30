import csv
from datetime import datetime
from bs4 import BeautifulSoup
import os

# Clase Stack para implementar la estructura de datos pila
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        else:
            return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def clear(self):
        self.items.clear()

# Clase Nodo para la lista doblemente enlazada de pestañas
class NodoPestania:
    def __init__(self, pestania):
        self.pestania = pestania
        self.prev = None
        self.next = None

# Clase Cola para implementar la estructura de datos cola
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        else:
            return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

# Clase Pagina que representa una página web
class Pagina:
    def __init__(self, url, contenido, fecha, hora):
        self.url = url
        self.contenido = contenido
        self.fecha = fecha
        self.hora = hora

# Clase HistorialNavegacion que gestiona el historial con pilas
class HistorialNavegacion:
    def __init__(self):
        self.pila_atras = Stack()     # Páginas para retroceder
        self.pila_adelante = Stack()  # Páginas para avanzar

    def visitar_pagina(self, pagina):
        self.pila_atras.push(pagina)
        self.pila_adelante.clear()

    def ir_atras(self):
        if self.pila_atras.size() > 1:
            pagina_actual = self.pila_atras.pop()
            self.pila_adelante.push(pagina_actual)
            return self.pila_atras.peek()
        else:
            print("No hay páginas anteriores.")
            return self.pila_atras.peek()

    def ir_adelante(self):
        if not self.pila_adelante.is_empty():
            pagina_siguiente = self.pila_adelante.pop()
            self.pila_atras.push(pagina_siguiente)
            return pagina_siguiente
        else:
            print("No hay páginas siguientes.")
            return self.pila_atras.peek()

    def pagina_actual(self):
        return self.pila_atras.peek()

    def mostrar_historial(self):
        temp_stack = Stack()
        historial = []

        # Vaciar pila_atras en temporal y guardar páginas
        while not self.pila_atras.is_empty():
            pagina = self.pila_atras.pop()
            historial.append(pagina)
            temp_stack.push(pagina)

        # Restaurar pila_atras
        while not temp_stack.is_empty():
            pagina = temp_stack.pop()
            self.pila_atras.push(pagina)

        # Mostrar historial en orden
        for pagina in reversed(historial):
            print(f"{pagina.fecha} {pagina.hora} - {pagina.url}")

# Clase Pestania que utiliza una instancia de HistorialNavegacion
class Pestania:
    def __init__(self, id_pestania):
        self.id_pestania = id_pestania
        self.historial = HistorialNavegacion()

# Clase Descarga que representa una descarga
class Descarga:
    def __init__(self, url, tamanio, fecha, estado='Pendiente'):
        self.url = url
        self.tamanio = tamanio
        self.fecha = fecha
        self.estado = estado

# Clase GestorDescargas que gestiona las descargas con una cola
class GestorDescargas:
    def __init__(self):
        self.cola_descargas = Queue()
        self.descargas_completadas = []
        self.cargar_descargas()

    def agregar_descarga(self, descarga):
        self.cola_descargas.enqueue(descarga)
        print(f"Descarga añadida: {descarga.url}")

    def procesar_descargas(self):
        while not self.cola_descargas.is_empty():
            descarga_actual = self.cola_descargas.dequeue()
            descarga_actual.estado = 'Completada'
            self.descargas_completadas.append(descarga_actual)
            self.guardar_en_descargas_csv(descarga_actual)
            print(f"Descarga completada: {descarga_actual.url}")

    def mostrar_descargas(self):
        print("Descargas Pendientes:")
        for idx, descarga in enumerate(self.cola_descargas.items):
            print(f"{idx+1}. {descarga.url} - Tamaño: {descarga.tamanio}MB - Fecha: {descarga.fecha} - Estado: {descarga.estado}")
        print("\nDescargas Completadas:")
        for descarga in self.descargas_completadas:
            print(f"{descarga.url} - Tamaño: {descarga.tamanio}MB - Fecha: {descarga.fecha} - Estado: {descarga.estado}")

    def cancelar_descarga(self, numero):
        if 0 <= numero < self.cola_descargas.size():
            descarga_cancelada = self.cola_descargas.items.pop(numero)
            print(f"Descarga cancelada: {descarga_cancelada.url}")
        else:
            print("Número de descarga inválido.")

    def guardar_en_descargas_csv(self, descarga):
        with open('descargas.csv', mode='a', newline='') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([descarga.url, descarga.tamanio, descarga.fecha, descarga.estado])

    def cargar_descargas(self):
        try:
            with open('descargas.csv', mode='r') as archivo:
                lector = csv.reader(archivo)
                for fila in lector:
                    url, tamanio, fecha, estado = fila
                    descarga = Descarga(url, (tamanio), fecha, estado)
                    if estado == 'Pendiente':
                        self.cola_descargas.enqueue(descarga)
                    else:
                        self.descargas_completadas.append(descarga)
        except FileNotFoundError:
            pass

# Clase Navegador que gestiona las pestañas con una lista doblemente enlazada
class Navegador:
    def __init__(self):
        self.head = None  # Primer nodo (pestaña)
        self.tail = None  # Último nodo (pestaña)
        self.pestania_actual = None
        self.id_pestania_counter = 0
        self.gestor_descargas = GestorDescargas()
        self.nueva_pestania()

    def nueva_pestania(self, url=None):
        self.id_pestania_counter += 1
        pestania = Pestania(self.id_pestania_counter)
        nuevo_nodo = NodoPestania(pestania)
        if not self.head:
            self.head = self.tail = nuevo_nodo
        else:
            self.tail.next = nuevo_nodo
            nuevo_nodo.prev = self.tail
            self.tail = nuevo_nodo
        self.pestania_actual = nuevo_nodo
        if url:
            self.ir(url)
        else:
            print(f"Abriste una nueva pestaña (Pestaña {pestania.id_pestania}).")

    def cambiar_pestania(self, id_pestania):
        nodo_actual = self.head
        while nodo_actual:
            if nodo_actual.pestania.id_pestania == id_pestania:
                self.pestania_actual = nodo_actual
                if nodo_actual.pestania.historial.pagina_actual():
                    print(f"Ahora estás en la pestaña con: {nodo_actual.pestania.historial.pagina_actual().url}")
                else:
                    print(f"Ahora estás en la pestaña {id_pestania} sin página cargada.")
                return
            nodo_actual = nodo_actual.next
        print(f"No existe la pestaña {id_pestania}.")

    def cerrar_pestania(self):
        if self.pestania_actual:
            id_pestania = self.pestania_actual.pestania.id_pestania
            if self.pestania_actual.prev:
                self.pestania_actual.prev.next = self.pestania_actual.next
            if self.pestania_actual.next:
                self.pestania_actual.next.prev = self.pestania_actual.prev
            if self.pestania_actual == self.head:
                self.head = self.pestania_actual.next
            if self.pestania_actual == self.tail:
                self.tail = self.pestania_actual.prev
            nodo_siguiente = self.pestania_actual.next or self.pestania_actual.prev
            self.pestania_actual = nodo_siguiente
            print(f"Cerraste la pestaña {id_pestania}.")
            if self.pestania_actual:
                if self.pestania_actual.pestania.historial.pagina_actual():
                    print(f"Ahora estás en la pestaña con: {self.pestania_actual.pestania.historial.pagina_actual().url}")
                else:
                    print(f"Ahora estás en la pestaña {self.pestania_actual.pestania.id_pestania} sin página cargada.")
            else:
                print("No hay más pestañas abiertas.")
        else:
            print("No hay ninguna pestaña abierta.")

    def mostrar_pestanias(self):
        print("Pestañas abiertas:")
        nodo_actual = self.head
        while nodo_actual:
            indicador = "-> " if nodo_actual == self.pestania_actual else "   "
            id_pestania = nodo_actual.pestania.id_pestania
            if nodo_actual.pestania.historial.pagina_actual():
                url_actual = nodo_actual.pestania.historial.pagina_actual().url
            else:
                url_actual = "Sin página"
            print(f"{indicador}{id_pestania}. {url_actual}")
            nodo_actual = nodo_actual.next

    def ir(self, url):
        contenido = cargar_contenido_pagina(url)
        if contenido is not None:
            fecha, hora = obtener_fecha_hora_actual()
            nueva_pagina = Pagina(url, contenido, fecha, hora)
            self.pestania_actual.pestania.historial.visitar_pagina(nueva_pagina)
            guardar_en_historial_csv(nueva_pagina)
            print(f"Visitando: {url}")
        else:
            print(f"No se pudo cargar la página: {url}")

    def atras(self):
        pagina = self.pestania_actual.pestania.historial.ir_atras()
        if pagina:
            print(f"Regresando a: {pagina.url}")

    def adelante(self):
        pagina = self.pestania_actual.pestania.historial.ir_adelante()
        if pagina:
            print(f"Avanzando a: {pagina.url}")

    def mostrar_historial(self):
        self.pestania_actual.pestania.historial.mostrar_historial()

    def mostrar_contenido(self, modo='basico'):
        pagina = self.pestania_actual.pestania.historial.pagina_actual()
        if pagina:
            if modo == 'basico':
                print(pagina.contenido)
            elif modo == 'texto_plano':
                soup = BeautifulSoup(pagina.contenido, 'html.parser')
                print(soup.get_text())
            else:
                print("Modo no reconocido. Usa 'basico' o 'texto_plano'.")
        else:
            print("No hay ninguna página cargada en la pestaña actual.")

    def listar_paginas(self):
        print("Páginas disponibles para visitar:")
        try:
            with open('host.txt', mode='r') as archivo:
                for linea in archivo:
                    partes = linea.strip().split()
                    if len(partes) == 3:
                        _, _, dominio = partes
                        print(f"- {dominio}")
        except FileNotFoundError:
            print("El archivo host.txt no existe.")

# Funciones auxiliares
def obtener_fecha_hora_actual():
    ahora = datetime.now()
    fecha = ahora.strftime('%Y-%m-%d')
    hora = ahora.strftime('%H:%M:%S')
    return fecha, hora

def obtener_ruta_desde_url(url):
    ruta = ''
    try:
        with open('host.txt', mode='r') as archivo:
            for linea in archivo:
                partes = linea.strip().split()
                if len(partes) == 3:
                    ruta_archivo, ip, dominio = partes
                    if dominio == url or ip == url:
                        ruta = ruta_archivo
                        break
        if ruta == '':
            print("La URL o IP no existe en el archivo host.")
    except FileNotFoundError:
        print("El archivo host.txt no existe.")
    return ruta

def cargar_contenido_pagina(url):
    ruta = obtener_ruta_desde_url(url)
    if ruta:
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as archivo:
                    contenido = archivo.read()
                return contenido
            except FileNotFoundError:
                print(f"No se encontró el archivo HTML en la ruta: {ruta}")
                return None
        else:
            print(f"La ruta especificada no existe: {ruta}")
            return None
    else:
        return None

def guardar_en_historial_csv(pagina):
    with open('historial.csv', mode='a', newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([pagina.fecha, pagina.hora, pagina.url])

# Función principal
def main():
    navegador = Navegador()
    print("Bienvenido al Simulador de Navegador Web en Consola.")
    print("Escribe un comando para comenzar. Usa 'ayuda' para ver la lista de comandos disponibles.")

    while True:
        comando_input = input("> ").strip()
        partes = comando_input.split()
        if not partes:
            continue
        comando = partes[0]
        args = partes[1:]

        if comando == "ir":
            if args:
                url = args[0]
                navegador.ir(url)
            else:
                print("Debes especificar una URL.")
        elif comando == "atrás":
            navegador.atras()
        elif comando == "adelante":
            navegador.adelante()
        elif comando == "mostrar_historial":
            navegador.mostrar_historial()
        elif comando == "nueva_pestania":
            if args:
                url = args[0]
                navegador.nueva_pestania(url)
            else:
                navegador.nueva_pestania()
        elif comando == "mostrar_pestanias":
            navegador.mostrar_pestanias()
        elif comando == "cambiar_pestania":
            if args:
                try:
                    id_pestania = int(args[0])
                    navegador.cambiar_pestania(id_pestania)
                except ValueError:
                    print("Debes introducir un número de pestaña válido.")
            else:
                print("Debes especificar el número de pestaña.")
        elif comando == "cerrar_pestania":
            navegador.cerrar_pestania()
        elif comando == "descargar":
            if args:
                url = args[0]
                tamanio = float(args[1]) if len(args) > 1 else 10.0  # Tamaño por defecto
                fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                descarga = Descarga(url, tamanio, fecha)
                navegador.gestor_descargas.agregar_descarga(descarga)
            else:
                print("Debes especificar una URL para descargar.")
        elif comando == "mostrar_descargas":
            navegador.gestor_descargas.mostrar_descargas()
        elif comando == "cancelar_descarga":
            if args:
                try:
                    numero = int(args[0]) - 1
                    navegador.gestor_descargas.cancelar_descarga(numero)
                except ValueError:
                    print("Debes introducir un número de descarga válido.")
            else:
                print("Debes especificar el número de la descarga a cancelar.")
        elif comando == "procesar_descargas":
            navegador.gestor_descargas.procesar_descargas()
        elif comando == "mostrar_contenido":
            modo = args[0] if args else 'basico'
            navegador.mostrar_contenido(modo)
        elif comando == "listar_paginas":
            navegador.listar_paginas()
        elif comando == "ayuda":
            print("Comandos disponibles:")
            print("  ir [url]                  - Visitar una página utilizando una URL o IP.")
            print("  atrás                     - Volver a la página anterior.")
            print("  adelante                  - Avanzar a la página siguiente.")
            print("  mostrar_historial         - Mostrar el historial de la pestaña actual.")
            print("  nueva_pestania [url]      - Abrir una nueva pestaña, opcionalmente con una URL.")
            print("  mostrar_pestanias         - Mostrar todas las pestañas abiertas.")
            print("  cambiar_pestania [número] - Cambiar a la pestaña especificada.")
            print("  cerrar_pestania           - Cerrar la pestaña actual.")
            print("  descargar [url] [tamaño]  - Iniciar la descarga de una URL (tamaño opcional).")
            print("  mostrar_descargas         - Mostrar el estado de las descargas.")
            print("  cancelar_descarga [número]- Cancelar la descarga número n.")
            print("  procesar_descargas        - Procesar todas las descargas en la cola.")
            print("  mostrar_contenido [modo]  - Mostrar el contenido de la página actual ('basico' o 'texto_plano').")
            print("  listar_paginas            - Listar todas las páginas .html disponibles.")
            print("  ayuda                     - Mostrar esta ayuda.")
            print("  salir                     - Salir del navegador.")
        elif comando == "salir":
            break
        else:
            print("Comando no reconocido. Escribe 'ayuda' para ver la lista de comandos.")

if __name__ == "__main__":
    main()

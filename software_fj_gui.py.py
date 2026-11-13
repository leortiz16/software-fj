"""
software_fj.py
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.
Todo el proyecto en UN SOLO ARCHIVO, orientado a objetos y SIN base de datos
(los datos viven en listas; los archivos se usan solo para el log de eventos y errores).

Conceptos aplicados: abstracción, herencia, polimorfismo, encapsulación,
métodos sobrescritos, parámetros opcionales (sobrecarga), excepciones
personalizadas, try/except/else/finally y encadenamiento de excepciones.

Incluye una INTERFAZ GRÁFICA con Tkinter (ventanas, cajas de texto y botones).
Ejecutar con:  py software_fj_gui.py
"""
# ======================================================================
# 1. IMPORTACIONES
# ======================================================================
import logging  # módulo estándar de Python para registrar mensajes en un archivo
import os       # módulo para trabajar con rutas de archivos
import re       # expresiones regulares, para validar el formato del correo
import tkinter as tk  # librería para crear ventanas, botones y cajas de texto
from tkinter import messagebox, ttk  # messagebox = ventanitas de aviso; ttk = widgets modernos (Combobox)
from abc import ABC, abstractmethod  # permiten crear clases y métodos abstractos


# ======================================================================
# 2. REGISTRO DE LOGS
# Para qué sirve: el enunciado pide que errores y eventos queden en un archivo.
# 'logging' agrega fecha, hora y nivel (INFO, WARNING, ERROR) automáticamente.
# ======================================================================
# Ruta del log: misma carpeta de este archivo, con nombre eventos.log
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eventos.log")


def crear_logger() -> logging.Logger:  # prepara y devuelve el logger
    logger = logging.getLogger("SoftwareFJ")  # obtiene (o crea) un logger con ese nombre
    logger.setLevel(logging.INFO)  # registra desde INFO hacia arriba
    if not logger.handlers:  # solo configura si aún no tiene destino (evita duplicados)
        manejador = logging.FileHandler(RUTA_LOG, encoding="utf-8")  # escribe en archivo (utf-8 = tildes y ñ)
        manejador.setFormatter(  # formato de cada línea: fecha | nivel | mensaje
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")
        )
        logger.addHandler(manejador)  # conecta el logger con el archivo
    return logger


log = crear_logger()  # objeto 'log' usado en todo el programa para registrar eventos


# ======================================================================
# 3. EXCEPCIONES PERSONALIZADAS
# Para qué sirve: cada tipo de error tiene su propia clase, así se atrapa
# por separado y el log dice exactamente qué pasó.
# ======================================================================
class ErrorSoftwareFJ(Exception):  # clase base; hereda de Exception (errores de Python)
    """Todas las excepciones del sistema heredan de esta; permite atrapar
    cualquier error propio con un solo except."""


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Datos del cliente inválidos (nombre corto, correo mal escrito, etc.)."""


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Falta un parámetro obligatorio (por ejemplo, no se indicó el cliente)."""


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Servicio con datos incorrectos (tarifa negativa, duración inválida, etc.)."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio existe pero no está disponible para reservar."""


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Intento de reserva incorrecto (datos incompletos, no se pudo confirmar)."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Operación no permitida (ej: confirmar o cancelar en un estado incorrecto)."""


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """El cálculo de costos dio un resultado imposible (negativo, descuento > 100%)."""


# ======================================================================
# 4. ENTIDAD (CLASE ABSTRACTA) Y CLIENTE
# Conceptos: ABSTRACCIÓN, HERENCIA y ENCAPSULACIÓN.
# ======================================================================
class Entidad(ABC):  # hereda de ABC => clase abstracta (no se puede instanciar)
    """Representa "cualquier cosa" del sistema que tiene un id. Solo sirve de molde."""

    def __init__(self, identificador: int):  # constructor: se ejecuta al crear el objeto
        self._id = identificador  # guarda el id (un guion bajo = uso interno)

    @property  # permite leer 'objeto.id' como atributo, sin poder modificarlo
    def id(self) -> int:
        return self._id  # devuelve el id guardado

    @abstractmethod  # obliga a las clases hijas a implementar este método
    def describir(self) -> str:
        """Cada hija debe explicar qué es (esto permite el polimorfismo)."""


class Cliente(Entidad):  # Cliente HEREDA de Entidad
    """Cliente con datos personales ENCAPSULADOS (privados con doble guion bajo)
    y validados cada vez que se asignan."""

    def __init__(self, identificador: int, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)  # llama al constructor del padre para guardar el id
        # Al usar self.nombre = ... se ejecuta el setter de abajo, que valida el dato
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    # ---------- nombre ----------
    @property  # getter: permite leer cliente.nombre
    def nombre(self) -> str:
        return self.__nombre  # __nombre es privado: no se toca desde fuera de la clase

    @nombre.setter  # setter: se ejecuta al hacer cliente.nombre = "..."
    def nombre(self, valor: str):
        if not isinstance(valor, str) or len(valor.strip()) < 3:  # texto de al menos 3 caracteres
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.")  # lanza el error
        self.__nombre = valor.strip().title()  # quita espacios y pone mayúscula inicial

    # ---------- correo ----------
    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        # fullmatch exige que TODO el texto cumpla el patrón: algo@algo.algo
        if not isinstance(valor, str) or not re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.]+", valor):
            raise ClienteInvalidoError(f"Correo inválido: '{valor}'.")
        self.__correo = valor.lower()  # lo guarda en minúsculas

    # ---------- teléfono ----------
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        # Solo dígitos y entre 7 y 10 caracteres
        if not isinstance(valor, str) or not valor.isdigit() or not 7 <= len(valor) <= 10:
            raise ClienteInvalidoError(f"Teléfono inválido: '{valor}' (7 a 10 dígitos).")
        self.__telefono = valor

    def describir(self) -> str:  # implementa el método abstracto del padre
        return f"Cliente #{self.id}: {self.nombre} | {self.correo} | Tel: {self.telefono}"


# ======================================================================
# 5. SERVICIOS (CLASE ABSTRACTA + 3 ESPECIALIZADOS)
# Conceptos: HERENCIA, POLIMORFISMO, MÉTODOS SOBRESCRITOS y SOBRECARGA
# (en Python se logra con parámetros que tienen valor por defecto).
# ======================================================================
IVA_POR_DEFECTO = 0.19  # constante: impuesto del 19% si no se indica otro


class Servicio(Entidad):  # abstracta: hereda de Entidad y deja un método abstracto pendiente
    """Define lo que TODO servicio debe tener y hacer."""

    def __init__(self, identificador: int, nombre: str, tarifa_hora: float, disponible: bool = True):
        super().__init__(identificador)  # guarda el id en la clase padre
        if not nombre or not nombre.strip():  # nombre vacío o solo espacios
            raise ServicioInvalidoError("El servicio necesita un nombre.")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:  # número mayor que cero
            raise ServicioInvalidoError(f"Tarifa por hora inválida: {tarifa_hora}")
        self._nombre = nombre.strip()  # guarda el nombre sin espacios sobrantes
        self._tarifa_hora = float(tarifa_hora)  # guarda la tarifa como decimal
        self._disponible = disponible  # True = se puede reservar

    @property
    def nombre(self) -> str:  # lectura del nombre
        return self._nombre

    @property
    def disponible(self) -> bool:  # lectura de la disponibilidad
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):  # permite cambiar la disponibilidad
        self._disponible = bool(valor)

    def validar_parametros(self, horas: float) -> None:
        """Validación común a todos: la duración debe ser un número positivo."""
        if horas is None:  # no se envió la duración
            raise ParametroFaltanteError("Falta indicar la duración en horas.")
        if not isinstance(horas, (int, float)) or horas <= 0:  # no es número o es <= 0
            raise ServicioInvalidoError(f"Duración inválida: {horas}")

    @abstractmethod  # cada hijo DEBE implementarlo a su manera (polimorfismo)
    def calcular_costo(self, horas: float, impuesto: float = IVA_POR_DEFECTO,
                       descuento: float = 0.0) -> float:
        """Parámetros con valor por defecto permiten llamarlo de varias formas:
            calcular_costo(2)                 -> solo con IVA
            calcular_costo(2, descuento=0.1)  -> con 10% de descuento
            calcular_costo(2, impuesto=0)     -> sin impuesto"""

    def _aplicar_impuesto_descuento(self, base: float, impuesto: float, descuento: float) -> float:
        """Método de apoyo (con _ = interno) para no repetir la cuenta en cada hijo."""
        if not 0 <= descuento < 1:  # el descuento debe estar entre 0% y menos de 100%
            raise CalculoInconsistenteError(f"Descuento fuera de rango: {descuento}")
        if impuesto < 0:  # un impuesto negativo no tiene sentido
            raise CalculoInconsistenteError(f"Impuesto negativo: {impuesto}")
        total = base * (1 - descuento) * (1 + impuesto)  # primero descuento, luego impuesto
        if total < 0:  # seguridad extra contra resultados imposibles
            raise CalculoInconsistenteError("El costo total resultó negativo.")
        return round(total, 2)  # redondea a 2 decimales


class ReservaSala(Servicio):  # SERVICIO 1
    """Reserva de salas. Cobra por hora y un recargo si la sala es grande."""

    def __init__(self, identificador: int, nombre: str, tarifa_hora: float, capacidad: int,
                 disponible: bool = True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)  # datos comunes en el padre
        if capacidad <= 0:  # una sala necesita capacidad positiva
            raise ServicioInvalidoError("La capacidad debe ser mayor a 0.")
        self._capacidad = capacidad  # dato propio de las salas

    def calcular_costo(self, horas, impuesto=IVA_POR_DEFECTO, descuento=0.0):  # SOBRESCRITO
        self.validar_parametros(horas)  # valida la duración antes de calcular
        base = self._tarifa_hora * horas  # costo básico: tarifa x horas
        if self._capacidad > 20:  # salas de más de 20 personas
            base *= 1.15  # recargo del 15%
        return self._aplicar_impuesto_descuento(base, impuesto, descuento)

    def describir(self) -> str:
        return f"Sala '{self.nombre}' (capacidad {self._capacidad}) - ${self._tarifa_hora:,.0f}/hora"


class AlquilerEquipo(Servicio):  # SERVICIO 2
    """Alquiler de equipos. Cobra por hora más un depósito fijo."""

    def __init__(self, identificador: int, nombre: str, tarifa_hora: float, deposito: float,
                 disponible: bool = True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        if deposito < 0:  # el depósito puede ser 0 pero no negativo
            raise ServicioInvalidoError("El depósito no puede ser negativo.")
        self._deposito = deposito  # dato propio de los equipos

    def calcular_costo(self, horas, impuesto=IVA_POR_DEFECTO, descuento=0.0):  # SOBRESCRITO
        self.validar_parametros(horas)
        base = self._tarifa_hora * horas + self._deposito  # horas + depósito fijo
        return self._aplicar_impuesto_descuento(base, impuesto, descuento)

    def describir(self) -> str:
        return f"Equipo '{self.nombre}' - ${self._tarifa_hora:,.0f}/hora + depósito ${self._deposito:,.0f}"


class Asesoria(Servicio):  # SERVICIO 3
    """Asesorías especializadas. El nivel del asesor cambia la tarifa."""

    FACTOR_NIVEL = {"junior": 1.0, "senior": 1.5, "experto": 2.0}  # multiplicador por nivel

    def __init__(self, identificador: int, nombre: str, tarifa_hora: float, nivel: str,
                 disponible: bool = True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        if nivel not in self.FACTOR_NIVEL:  # el nivel debe existir en el diccionario
            raise ServicioInvalidoError(f"Nivel de asesor desconocido: '{nivel}'")
        self._nivel = nivel  # dato propio de las asesorías

    def validar_parametros(self, horas):  # SOBRESCRIBE el método del padre
        """Usa la validación del padre y agrega una regla propia."""
        super().validar_parametros(horas)  # primero las reglas generales
        if horas > 8:  # regla propia: máximo 8 horas
            raise ServicioInvalidoError("Una asesoría no puede durar más de 8 horas.")

    def calcular_costo(self, horas, impuesto=IVA_POR_DEFECTO, descuento=0.0):  # SOBRESCRITO
        self.validar_parametros(horas)  # usa la validación propia de esta clase
        base = self._tarifa_hora * horas * self.FACTOR_NIVEL[self._nivel]  # tarifa x horas x nivel
        return self._aplicar_impuesto_descuento(base, impuesto, descuento)

    def describir(self) -> str:
        return f"Asesoría '{self.nombre}' (nivel {self._nivel}) - ${self._tarifa_hora:,.0f}/hora base"


# ======================================================================
# 6. RESERVA
# Une cliente + servicio + duración + estado. Usa try/except/else/finally
# y ENCADENAMIENTO de excepciones (raise ... from ...).
# ======================================================================
PENDIENTE, CONFIRMADA, CANCELADA = "PENDIENTE", "CONFIRMADA", "CANCELADA"  # estados posibles


class Reserva(Entidad):  # hereda de Entidad (tiene id y describir)
    def __init__(self, identificador: int, cliente: Cliente, servicio: Servicio, horas: float):
        super().__init__(identificador)  # guarda el id
        if cliente is None or servicio is None:  # faltan datos obligatorios
            raise ParametroFaltanteError("Una reserva necesita cliente y servicio.")
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):  # tipos correctos
            raise ReservaInvalidaError("Cliente o servicio con tipo incorrecto.")
        self.cliente = cliente  # quién reserva
        self.servicio = servicio  # qué reserva
        self.horas = horas  # duración
        self._estado = PENDIENTE  # toda reserva nace pendiente
        self.costo = None  # se calcula al confirmar

    @property
    def estado(self) -> str:  # lectura del estado (no se modifica desde fuera)
        return self._estado

    def confirmar(self) -> None:
        """PENDIENTE -> CONFIRMADA. Verifica disponibilidad y calcula el costo."""
        if self._estado != PENDIENTE:  # solo se confirma lo que está pendiente
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self._estado}.")
        if not self.servicio.disponible:  # el servicio debe estar abierto
            raise ServicioNoDisponibleError(f"'{self.servicio.nombre}' no está disponible.")
        try:  # intenta calcular el costo (puede fallar si la duración es mala)
            self.costo = self.servicio.calcular_costo(self.horas)
        except ErrorSoftwareFJ as error:
            # ENCADENAMIENTO: "from error" conserva la causa original en el error nuevo
            raise ReservaInvalidaError("No se pudo confirmar por un problema en el cálculo.") from error
        self._estado = CONFIRMADA  # si todo salió bien, queda confirmada

    def cancelar(self) -> None:
        if self._estado == CANCELADA:  # no se puede cancelar dos veces
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada.")
        self._estado = CANCELADA  # cambia el estado

    def procesar(self) -> bool:
        """Intenta confirmar con try/except/else/finally. Devuelve True si salió bien.
        - try:     código que puede fallar
        - except:  qué hacer si falla (se registra en el log y el programa sigue)
        - else:    se ejecuta SOLO si no hubo error
        - finally: se ejecuta SIEMPRE, haya error o no"""
        try:
            self.confirmar()  # intento principal
        except (ServicioNoDisponibleError, OperacionNoPermitidaError) as e:  # errores esperables
            log.warning(f"Reserva #{self.id} no procesada: {e}")
            return False
        except ReservaInvalidaError as e:  # error grave por cálculo
            # e.__cause__ es el error original gracias al encadenamiento
            log.error(f"Reserva #{self.id} falló: {e} | causa: {e.__cause__!r}")
            return False
        else:  # solo si NO hubo excepción
            log.info(f"Reserva #{self.id} confirmada. Costo total: ${self.costo:,.2f}")
            return True
        finally:  # siempre se ejecuta, incluso después de un return
            log.info(f"Fin del procesamiento de la reserva #{self.id} (estado: {self._estado})")

    def describir(self) -> str:  # implementa el método abstracto de Entidad
        costo = f"${self.costo:,.2f}" if self.costo is not None else "sin calcular"
        return (f"Reserva #{self.id} [{self._estado}] {self.cliente.nombre} -> "
                f"{self.servicio.nombre} x {self.horas}h | {costo}")


# ======================================================================
# 7. GESTOR (guarda todo en LISTAS, sin base de datos)
# ======================================================================
class GestorSoftwareFJ:
    """Administra clientes, servicios y reservas en listas internas."""

    def __init__(self):
        self.clientes: list[Cliente] = []  # lista de clientes registrados
        self.servicios: list = []  # lista de servicios creados
        self.reservas: list[Reserva] = []  # lista de reservas hechas

    def ejecutar(self, descripcion: str, accion, salida=print):
        """Ejecuta una operación dentro de try/except para que un error NUNCA detenga el programa.
        'accion' es una función (lambda) que se llama dentro del try.
        'salida' es la función que muestra los mensajes (print en consola, o la caja de texto en la ventana).
        Devuelve (exito, texto) para que la ventana pueda mostrar un aviso si hubo error."""
        salida(f">> {descripcion}")  # muestra qué operación se hace
        try:
            resultado = accion()  # ejecuta la operación
        except ErrorSoftwareFJ as e:  # errores propios del sistema (esperados)
            log.error(f"{descripcion} -> {type(e).__name__}: {e}")  # los guarda en el log
            texto = f"[ERROR CONTROLADO] {type(e).__name__}: {e}"
            salida("   " + texto)
            return False, str(e)
        except Exception as e:  # cualquier otro error imprevisto
            log.critical(f"{descripcion} -> ERROR INESPERADO {type(e).__name__}: {e}")
            texto = f"[ERROR INESPERADO] {type(e).__name__}: {e}"
            salida("   " + texto)
            return False, str(e)
        else:  # solo si no hubo error
            log.info(f"{descripcion} -> OK")
            salida(f"   [OK] {resultado}")
            return True, str(resultado)
        finally:  # siempre se ejecuta
            salida("   (el sistema continúa activo)")

    def registrar_cliente(self, *datos) -> str:  # *datos recibe nombre, correo, teléfono
        cliente = Cliente(len(self.clientes) + 1, *datos)  # id = cantidad actual + 1
        self.clientes.append(cliente)  # solo se agrega si el constructor no falló
        return cliente.describir()

    def registrar_servicio(self, servicio) -> str:
        self.servicios.append(servicio)  # agrega el servicio a la lista
        return servicio.describir()

    def crear_reserva(self, cliente, servicio, horas) -> str:
        reserva = Reserva(len(self.reservas) + 1, cliente, servicio, horas)  # puede lanzar error
        self.reservas.append(reserva)  # queda registrada aunque no se confirme
        if not reserva.procesar():  # procesar() devuelve False si falló
            # Se lanza error para que la operación quede marcada como FALLIDA en el log
            raise ReservaInvalidaError(f"La reserva #{reserva.id} no pudo confirmarse.")
        return reserva.describir()


# ======================================================================
# 8. SIMULACIÓN DE 15 OPERACIONES (válidas e inválidas)
# Recibe un gestor y una función 'salida' para mostrar los mensajes.
# ======================================================================
def simular_operaciones(g: GestorSoftwareFJ, salida=print):
    log.info("=== Inicio de la simulación Software FJ ===")
    ej = lambda desc, accion: g.ejecutar(desc, accion, salida)  # atajo para escribir menos

    # Operaciones 1-3: clientes (2 válidos y 1 inválido)
    ej("1. Registrar cliente válido (Ana)", lambda: g.registrar_cliente("ana gómez", "ana@correo.com", "3001234567"))
    ej("2. Registrar cliente válido (Luis)", lambda: g.registrar_cliente("Luis Pérez", "luis@correo.com", "3109876543"))
    ej("3. Registrar cliente INVÁLIDO (correo malo)", lambda: g.registrar_cliente("Pedro Ruiz", "pedro-correo", "3115555555"))

    # Operaciones 4-7: servicios (3 válidos y 1 inválido)
    ej("4. Crear sala", lambda: g.registrar_servicio(ReservaSala(1, "Sala Amazonas", 50000, 30)))
    ej("5. Crear equipo", lambda: g.registrar_servicio(AlquilerEquipo(2, "Proyector HD", 15000, 40000)))
    ej("6. Crear asesoría", lambda: g.registrar_servicio(Asesoria(3, "Asesoría en Redes", 80000, "senior")))
    ej("7. Crear servicio INVÁLIDO (tarifa negativa)", lambda: g.registrar_servicio(ReservaSala(4, "Sala Rota", -100, 10)))

    # Servicio no disponible, creado aparte para probar el error de disponibilidad
    sala_cerrada = ReservaSala(5, "Sala en mantenimiento", 40000, 10, disponible=False)
    g.servicios.append(sala_cerrada)

    # Atajos a los objetos creados arriba (posiciones en las listas)
    ana, luis = g.clientes[0], g.clientes[1]
    sala, proyector, asesoria = g.servicios[0], g.servicios[1], g.servicios[2]

    # Operaciones 8-12: reservas (2 exitosas y 3 fallidas)
    ej("8. Reserva exitosa de sala (3h)", lambda: g.crear_reserva(ana, sala, 3))
    ej("9. Reserva exitosa de equipo (2h)", lambda: g.crear_reserva(luis, proyector, 2))
    ej("10. Reserva FALLIDA: servicio no disponible", lambda: g.crear_reserva(ana, sala_cerrada, 2))
    ej("11. Reserva FALLIDA: duración inválida (-4h)", lambda: g.crear_reserva(luis, asesoria, -4))
    ej("12. Reserva FALLIDA: falta el cliente", lambda: g.crear_reserva(None, sala, 2))

    # Operaciones 13-15: cancelación y cálculos
    ej("13. Cancelar dos veces la misma reserva", lambda: (g.reservas[0].cancelar(), g.reservas[0].cancelar()))
    ej("14. Costo con descuento del 10% y sin IVA", lambda: f"${asesoria.calcular_costo(2, impuesto=0, descuento=0.10):,.2f}")
    ej("15. Descuento absurdo (150%)", lambda: asesoria.calcular_costo(2, descuento=1.5))

    log.info("=== Fin de la simulación ===")


# ======================================================================
# 9. INTERFAZ GRÁFICA (Tkinter)
# Para qué sirve: en vez de usar la terminal, el usuario trabaja con
# ventanas, cajas de texto (Entry) y botones (Button).
# ======================================================================
class AplicacionFJ:
    """Ventana principal. Guarda un gestor y construye todos los widgets."""

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz  # ventana principal (Tk) recibida desde main()
        self.raiz.title("Software FJ - Clientes, Servicios y Reservas")  # título de la ventana
        self.raiz.geometry("980x700")  # tamaño inicial: ancho x alto
        self.g = GestorSoftwareFJ()  # el gestor con las listas internas (sin base de datos)
        self._crear_widgets()  # arma toda la ventana
        self.escribir("Bienvenido a Software FJ. Los eventos se guardan en eventos.log")

    # ---------- construcción de la ventana ----------
    def _crear_widgets(self):
        # Frame = contenedor para agrupar widgets; LabelFrame = contenedor con título
        izquierda = ttk.Frame(self.raiz, padding=8)  # columna izquierda: formularios
        izquierda.pack(side="left", fill="y")
        derecha = ttk.Frame(self.raiz, padding=8)  # columna derecha: listas y mensajes
        derecha.pack(side="right", fill="both", expand=True)

        # --- Formulario de CLIENTE ---
        marco_c = ttk.LabelFrame(izquierda, text="Registrar cliente", padding=8)
        marco_c.pack(fill="x", pady=4)
        self.e_nombre = self._campo(marco_c, "Nombre", 0)  # Entry = caja de texto
        self.e_correo = self._campo(marco_c, "Correo", 1)
        self.e_tel = self._campo(marco_c, "Teléfono", 2)
        ttk.Button(marco_c, text="Registrar cliente", command=self.registrar_cliente).grid(
            row=3, column=0, columnspan=2, pady=6)  # Button = botón; command = función que ejecuta al pulsar

        # --- Formulario de SERVICIO ---
        marco_s = ttk.LabelFrame(izquierda, text="Crear servicio", padding=8)
        marco_s.pack(fill="x", pady=4)
        ttk.Label(marco_s, text="Tipo").grid(row=0, column=0, sticky="w")  # Label = texto fijo
        self.c_tipo = ttk.Combobox(marco_s, values=["Sala", "Equipo", "Asesoría"], state="readonly", width=18)
        self.c_tipo.current(0)  # selecciona "Sala" por defecto
        self.c_tipo.grid(row=0, column=1, pady=2)  # Combobox = lista desplegable
        self.e_snombre = self._campo(marco_s, "Nombre", 1)
        self.e_tarifa = self._campo(marco_s, "Tarifa por hora", 2)
        self.e_extra = self._campo(marco_s, "Capacidad / Depósito / Nivel", 3)
        self.var_disp = tk.BooleanVar(value=True)  # variable ligada al Checkbutton (True/False)
        ttk.Checkbutton(marco_s, text="Disponible", variable=self.var_disp).grid(row=4, column=0, columnspan=2)
        ttk.Button(marco_s, text="Crear servicio", command=self.crear_servicio).grid(
            row=5, column=0, columnspan=2, pady=6)

        # --- Formulario de RESERVA ---
        marco_r = ttk.LabelFrame(izquierda, text="Nueva reserva", padding=8)
        marco_r.pack(fill="x", pady=4)
        ttk.Label(marco_r, text="Cliente").grid(row=0, column=0, sticky="w")
        self.c_cliente = ttk.Combobox(marco_r, state="readonly", width=24)
        self.c_cliente.grid(row=0, column=1, pady=2)
        ttk.Label(marco_r, text="Servicio").grid(row=1, column=0, sticky="w")
        self.c_servicio = ttk.Combobox(marco_r, state="readonly", width=24)
        self.c_servicio.grid(row=1, column=1, pady=2)
        self.e_horas = self._campo(marco_r, "Horas", 2)
        ttk.Button(marco_r, text="Crear y procesar reserva", command=self.crear_reserva).grid(
            row=3, column=0, columnspan=2, pady=6)

        # --- Lista de reservas (Listbox) ---
        ttk.Label(derecha, text="Reservas").pack(anchor="w")
        self.lista = tk.Listbox(derecha, height=8)  # Listbox = lista donde se elige una fila
        self.lista.pack(fill="x")
        botones = ttk.Frame(derecha)
        botones.pack(fill="x", pady=4)
        ttk.Button(botones, text="Cancelar reserva seleccionada", command=self.cancelar_reserva).pack(side="left")
        ttk.Button(botones, text="Ejecutar simulación (15 operaciones)", command=self.simular).pack(side="left", padx=6)

        # --- Caja de mensajes (Text con barra de desplazamiento) ---
        ttk.Label(derecha, text="Registro de eventos").pack(anchor="w")
        self.texto = tk.Text(derecha, height=18, state="disabled")  # Text = caja de varias líneas (solo lectura)
        barra = ttk.Scrollbar(derecha, command=self.texto.yview)  # Scrollbar = barra para subir y bajar
        self.texto.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.texto.pack(fill="both", expand=True)

    def _campo(self, marco, etiqueta: str, fila: int) -> ttk.Entry:
        """Crea una etiqueta y una caja de texto en la fila indicada (evita repetir código)."""
        ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w")
        entrada = ttk.Entry(marco, width=26)
        entrada.grid(row=fila, column=1, pady=2)
        return entrada

    # ---------- utilidades de la ventana ----------
    def escribir(self, mensaje: str):
        """Agrega una línea a la caja de mensajes."""
        self.texto.configure(state="normal")  # se habilita para poder escribir
        self.texto.insert("end", mensaje + "\n")  # inserta al final
        self.texto.see("end")  # baja automáticamente al último mensaje
        self.texto.configure(state="disabled")  # vuelve a solo lectura

    def refrescar(self):
        """Actualiza las listas desplegables y el Listbox con lo que hay en las listas del gestor."""
        self.c_cliente["values"] = [f"{c.id} - {c.nombre}" for c in self.g.clientes]
        self.c_servicio["values"] = [f"{s.id} - {s.nombre}" for s in self.g.servicios]
        self.lista.delete(0, "end")  # borra todo el contenido anterior
        for r in self.g.reservas:
            self.lista.insert("end", r.describir())  # agrega una fila por reserva

    def _ejecutar(self, descripcion: str, accion) -> bool:
        """Ejecuta una acción con manejo de errores; si falla, muestra un aviso emergente."""
        exito, texto = self.g.ejecutar(descripcion, accion, self.escribir)
        if not exito:
            messagebox.showerror("Error controlado", texto)  # ventanita de error
        self.refrescar()  # actualiza las listas de la pantalla
        return exito

    # ---------- acciones de los botones ----------
    def registrar_cliente(self):
        self._ejecutar("Registrar cliente", lambda: self.g.registrar_cliente(
            self.e_nombre.get(), self.e_correo.get(), self.e_tel.get()))  # .get() lee el texto de la caja

    def crear_servicio(self):
        def construir():  # función interna: arma el servicio según el tipo elegido
            tipo, nombre = self.c_tipo.get(), self.e_snombre.get()
            try:
                tarifa = float(self.e_tarifa.get())  # convierte el texto a número
            except ValueError:  # si escribieron letras en vez de número
                raise ServicioInvalidoError("La tarifa debe ser un número.") from None
            extra, disp, nuevo_id = self.e_extra.get().strip(), self.var_disp.get(), len(self.g.servicios) + 1
            if tipo == "Sala":
                servicio = ReservaSala(nuevo_id, nombre, tarifa, int(extra or 0), disp)
            elif tipo == "Equipo":
                servicio = AlquilerEquipo(nuevo_id, nombre, tarifa, float(extra or 0), disp)
            else:
                servicio = Asesoria(nuevo_id, nombre, tarifa, extra.lower(), disp)
            return self.g.registrar_servicio(servicio)
        self._ejecutar("Crear servicio", construir)

    def crear_reserva(self):
        def construir():
            i_c, i_s = self.c_cliente.current(), self.c_servicio.current()  # posición elegida (-1 si no hay)
            if i_c < 0 or i_s < 0:
                raise ParametroFaltanteError("Debes elegir un cliente y un servicio.")
            try:
                horas = float(self.e_horas.get())
            except ValueError:
                raise ReservaInvalidaError("Las horas deben ser un número.") from None
            return self.g.crear_reserva(self.g.clientes[i_c], self.g.servicios[i_s], horas)
        self._ejecutar("Crear reserva", construir)

    def cancelar_reserva(self):
        def construir():
            seleccion = self.lista.curselection()  # filas elegidas en el Listbox
            if not seleccion:
                raise ParametroFaltanteError("Selecciona una reserva de la lista.")
            reserva = self.g.reservas[seleccion[0]]
            reserva.cancelar()
            return reserva.describir()
        self._ejecutar("Cancelar reserva", construir)

    def simular(self):
        """Reinicia el gestor y corre las 15 operaciones, mostrando todo en la caja de mensajes."""
        self.g = GestorSoftwareFJ()  # lista vacía nueva
        simular_operaciones(self.g, self.escribir)
        self.refrescar()
        messagebox.showinfo("Simulación terminada", "Se ejecutaron 15 operaciones.\nRevisa el archivo eventos.log.")


def main():
    raiz = tk.Tk()  # crea la ventana principal de Tkinter
    AplicacionFJ(raiz)  # construye la aplicación dentro de esa ventana
    raiz.mainloop()  # mantiene la ventana abierta esperando clics (bucle de eventos)


if __name__ == "__main__":  # solo abre la ventana si ejecutas este archivo directamente
    main()

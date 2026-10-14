
import tkinter as tk
import math

# ==========================================
# CONFIGURACION
# ==========================================

FONDO = "#f1f5f9"
AZUL = "#2563eb"
VERDE = "#16a34a"
ROJO = "#dc2626"
TEXTO = "#172033"

W, H = 850, 530

ventana = tk.Tk()
ventana.title("MathGraph | Calculadora matematica")
ventana.geometry("1000x850")
ventana.minsize(850, 750)
ventana.configure(bg=FONDO)

tipo = None
campos = {}
grafica = None
resultado = None
panel_datos = None


# ==========================================
# ENCABEZADO
# ==========================================

tk.Label(
    ventana,
    text="MathGraph",
    font=("Arial", 28, "bold"),
    bg=FONDO, fg=AZUL
).pack(pady=(15, 0))

tk.Label(
    ventana,
    text="Calculadora de ecuaciones y graficas",
    font=("Arial", 12),
    bg=FONDO, fg="#64748b"
).pack(pady=(0, 15))


# ==========================================
# FUNCIONES DE INTERFAZ
# ==========================================

zona = tk.Frame(ventana, bg=FONDO)
zona.pack(fill="x", padx=20)

def limpiar_zona():
    for widget in zona.winfo_children():
        widget.destroy()

def crear_campo(contenedor, etiqueta, valor="0"):
    marco = tk.Frame(contenedor, bg="white")
    marco.pack(side="left", padx=10, pady=10)

    tk.Label(
        marco, text=etiqueta,
        font=("Arial", 12, "bold"),
        bg="white", fg=TEXTO
    ).pack()

    entrada = tk.Entry(
        marco, width=10,
        font=("Arial", 15), justify="center"
    )
    entrada.insert(0, valor)
    entrada.pack(pady=5)

    campos[etiqueta] = entrada


def volver_menu():
    global tipo
    tipo = None
    campos.clear()

    for widget in ventana.winfo_children():
        if widget not in (zona,):
            widget.destroy()

    # Reconstruir la interfaz inicial
    iniciar_menu()


def iniciar_menu():
    global tipo

    limpiar_zona()
    campos.clear()

    tk.Label(
        zona,
        text="1. ELIGE EL TIPO DE ECUACION",
        font=("Arial", 15, "bold"),
        bg=FONDO, fg=TEXTO
    ).pack(pady=10)

    tk.Button(
        zona,
        text="ECUACION LINEAL",
        font=("Arial", 14, "bold"),
        bg=AZUL, fg="white",
        activebackground=AZUL,
        command=lambda: seleccionar("lineal"),
        padx=20, pady=12
    ).pack(pady=8)

    tk.Label(
        zona,
        text="Forma: y = mx + b",
        font=("Arial", 12),
        bg=FONDO
    ).pack()

    tk.Button(
        zona,
        text="ECUACION CUADRATICA",
        font=("Arial", 14, "bold"),
        bg=VERDE, fg="white",
        activebackground=VERDE,
        command=lambda: seleccionar("cuadratica"),
        padx=20, pady=12
    ).pack(pady=8)

    tk.Label(
        zona,
        text="Forma: y = ax² + bx + c",
        font=("Arial", 12),
        bg=FONDO
    ).pack(pady=(0, 15))


def seleccionar(eleccion):
    global tipo, grafica, resultado, panel_datos

    tipo = eleccion
    limpiar_zona()
    campos.clear()

    nombre = "LINEAL" if tipo == "lineal" else "CUADRATICA"

    tk.Label(
        zona,
        text=f"2. ECUACION {nombre}",
        font=("Arial", 16, "bold"),
        bg=FONDO, fg=TEXTO
    ).pack(pady=8)

    tk.Label(
        zona,
        text=("y = mx + b" if tipo == "lineal"
              else "y = ax² + bx + c"),
        font=("Arial", 14),
        bg=FONDO, fg=AZUL
    ).pack()

    marco_campos = tk.Frame(zona, bg="white")
    marco_campos.pack(pady=8)

    if tipo == "lineal":
        crear_campo(marco_campos, "m", "2")
        crear_campo(marco_campos, "b", "3")
    else:
        crear_campo(marco_campos, "a", "1")
        crear_campo(marco_campos, "b", "0")
        crear_campo(marco_campos, "c", "-4")

    tk.Button(
        zona,
        text="CALCULAR Y GRAFICAR",
        font=("Arial", 13, "bold"),
        bg=AZUL, fg="white",
        command=calcular,
        padx=18, pady=9
    ).pack(pady=8)

    tk.Button(
        zona,
        text="← Elegir otro tipo de ecuacion",
        font=("Arial", 10),
        command=iniciar_menu
    ).pack(pady=3)

    panel_datos = tk.Frame(ventana, bg="white")
    panel_datos.pack(fill="both", expand=True, padx=20, pady=12)

    grafica = tk.Canvas(
        panel_datos, width=W, height=H,
        bg="white", highlightthickness=0
    )
    grafica.pack(fill="both", expand=True, padx=8, pady=8)

    resultado = tk.Label(
        ventana,
        text="Introduce los coeficientes.",
        font=("Arial", 12),
        bg=FONDO, fg=TEXTO,
        justify="left", wraplength=950
    )
    resultado.pack(pady=8)


# ==========================================
# ESCALA AUTOMATICA DE LOS EJES
# ==========================================

def paso_bonito(rango):
    if rango <= 0 or not math.isfinite(rango):
        return 1

    bruto = rango / 8
    potencia = 10 ** math.floor(math.log10(bruto))
    fraccion = bruto / potencia

    if fraccion <= 1:
        base = 1
    elif fraccion <= 2:
        base = 2
    elif fraccion <= 5:
        base = 5
    else:
        base = 10

    return base * potencia


def dibujar(a, b, c, es_lineal):
    grafica.delete("all")

    ancho = max(grafica.winfo_width(), 400)
    alto = max(grafica.winfo_height(), 300)

    # Ajustar el intervalo horizontal a las raices
    # y al vertice cuando existan.
    importantes = [0.0]

    if es_lineal:
        if b != 0:
            importantes.append(-c / b)
    else:
        xv = -b / (2*a)
        importantes.append(xv)

        d = b*b - 4*a*c
        if d >= 0:
            r1 = (-b + math.sqrt(d)) / (2*a)
            r2 = (-b - math.sqrt(d)) / (2*a)
            importantes.extend([r1, r2])

    centro_min = min(importantes)
    centro_max = max(importantes)
    extension = max(5.0, (centro_max - centro_min) * 0.35)

    xmin = centro_min - extension
    xmax = centro_max + extension

    # Evitar intervalos demasiado grandes o diminutos
    xmin = max(xmin, -1e9)
    xmax = min(xmax, 1e9)

    if xmax - xmin < 2:
        xmin, xmax = -5, 5

    # Calcular los valores visibles de la funcion.
    muestras = []
    for i in range(1001):
        x = xmin + (xmax - xmin) * i / 1000
        y = a*x*x + b*x + c
        if math.isfinite(y):
            muestras.append(y)

    if not muestras:
        raise ValueError("Los valores son demasiado grandes.")

    ymin = min(muestras + [0.0])
    ymax = max(muestras + [0.0])

    if abs(ymax - ymin) < 1e-9:
        ymin -= 5
        ymax += 5
    else:
        margen = (ymax - ymin) * 0.12
        ymin -= margen
        ymax += margen

    # Conversion de coordenadas matematicas a pixeles
    def X(x):
        return (x - xmin) / (xmax - xmin) * ancho

    def Y(y):
        return alto - (y - ymin) / (ymax - ymin) * alto

    dx = paso_bonito(xmax - xmin)
    dy = paso_bonito(ymax - ymin)

    # Cuadricula vertical con numeros
    x = math.ceil(xmin / dx) * dx
    while x <= xmax:
        xx = X(x)
        grafica.create_line(
            xx, 0, xx, alto, fill="#e2e8f0"
        )

        if abs(x) > dx * 1e-8:
            grafica.create_text(
                xx, min(max(Y(0) + 16, 12), alto - 12),
                text=f"{x:g}", fill="#475569",
                font=("Arial", 9)
            )
        x += dx

    # Cuadricula horizontal con numeros
    y = math.ceil(ymin / dy) * dy
    while y <= ymax:
        yy = Y(y)
        grafica.create_line(
            0, yy, ancho, yy, fill="#e2e8f0"
        )

        if abs(y) > dy * 1e-8:
            grafica.create_text(
                min(max(X(0) - 22, 18), ancho - 18),
                yy, text=f"{y:g}", fill="#475569",
                font=("Arial", 9)
            )
        y += dy

    # Ejes X e Y
    if ymin <= 0 <= ymax:
        grafica.create_line(
            0, Y(0), ancho, Y(0),
            fill="#334155", width=2
        )
    if xmin <= 0 <= xmax:
        grafica.create_line(
            X(0), 0, X(0), alto,
            fill="#334155", width=2
        )

    # Curva dibujada con segmentos
    anterior = None
    for i in range(2001):
        x = xmin + (xmax - xmin) * i / 2000
        y = a*x*x + b*x + c

        if math.isfinite(y) and ymin <= y <= ymax:
            punto = (X(x), Y(y))
            if anterior:
                grafica.create_line(
                    anterior[0], anterior[1],
                    punto[0], punto[1],
                    fill=AZUL, width=3
                )
            anterior = punto
        else:
            anterior = None

    # Marcar las raices reales que sean visibles
    if es_lineal:
        raices = [-c / b] if b != 0 else []
    else:
        d = b*b - 4*a*c
        if d > 0:
            raices = [
                (-b + math.sqrt(d)) / (2*a),
                (-b - math.sqrt(d)) / (2*a)
            ]
        elif d == 0:
            raices = [-b / (2*a)]
        else:
            raices = []

    for r in raices:
        if xmin <= r <= xmax and ymin <= 0 <= ymax:
            grafica.create_oval(
                X(r)-5, Y(0)-5, X(r)+5, Y(0)+5,
                fill=ROJO, outline=ROJO
            )

    if not es_lineal:
        xv = -b / (2*a)
        yv = a*xv*xv + b*xv + c
        if xmin <= xv <= xmax and ymin <= yv <= ymax:
            grafica.create_oval(
                X(xv)-5, Y(yv)-5, X(xv)+5, Y(yv)+5,
                fill=VERDE, outline=VERDE
            )

    grafica.create_text(
        55, 15, text="y = f(x)",
        fill=AZUL, font=("Arial", 11, "bold")
    )


# ==========================================
# RESOLVER ECUACIONES
# ==========================================

def calcular():
    try:
        if tipo == "lineal":
            m = float(campos["m"].get())
            b = float(campos["b"].get())

            if not all(map(math.isfinite, [m, b])):
                raise ValueError

            if m == 0:
                dibujar(0, 0, b, False)
                mensaje = (
                    "La ecuacion es y = " + str(b) +
                    "\nEs una recta horizontal."
                )
                if b == 0:
                    mensaje += "\nTodos los valores de x son soluciones de y=0."
                else:
                    mensaje += "\nNo corta el eje X."
            else:
                # y = mx + b equivale a a=0, b=m, c=b
                dibujar(0, m, b, True)
                raiz = -b / m
                mensaje = (
                    f"Ecuacion: y = {m}x + {b}\n"
                    f"Pendiente: {m}\n"
                    f"Corte con Y: (0, {b})\n"
                    f"Raiz: x = {raiz:.6g}"
                )

            resultado.config(text=mensaje)

        else:
            a = float(campos["a"].get())
            b = float(campos["b"].get())
            c = float(campos["c"].get())

            if not all(map(math.isfinite, [a, b, c])):
                raise ValueError

            if a == 0:
                resultado.config(
                    text="Para una cuadratica, a debe ser distinto de cero."
                )
                return

            dibujar(a, b, c, False)

            d = b*b - 4*a*c
            xv = -b / (2*a)
            yv = a*xv*xv + b*xv + c

            mensaje = (
                f"Ecuacion: y = {a}x² + {b}x + {c}\n"
                f"Discriminante: {d:.6g}\n"
                f"Vertice: ({xv:.6g}, {yv:.6g})\n"
                f"Concavidad: {'hacia arriba' if a > 0 else 'hacia abajo'}"
            )

            if d > 0:
                r1 = (-b + math.sqrt(d)) / (2*a)
                r2 = (-b - math.sqrt(d)) / (2*a)
                mensaje += f"\nRaices: x1 = {r1:.6g}, x2 = {r2:.6g}"
            elif d == 0:
                mensaje += f"\nRaiz doble: x = {xv:.6g}"
            else:
                mensaje += "\nNo existen raices reales."

            resultado.config(text=mensaje)

    except (ValueError, OverflowError, ZeroDivisionError):
        resultado.config(
            text="Error: revisa los coeficientes e introduce numeros validos."
        )


# Iniciar en el menu de seleccion
iniciar_menu()
ventana.mainloop()

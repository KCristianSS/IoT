import mysql.connector
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

# Configuración de conexión
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'parcial2',
    'port': '3306'
}

# Diccionario de colores LED
led_colores = {1: 'green', 2: 'orange', 3: 'red'}

# Crear ventana principal
root = tk.Tk()
root.title("Dashboard IoT")

# Función para obtener datos
def obtener_datos():
    conexion = mysql.connector.connect(**config)
    cursor = conexion.cursor()
    consulta = "SELECT hora_fecha, temperatura, humedad, distancia, color_led FROM sensores ORDER BY id DESC LIMIT 20"
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultados[::-1]

# ABM Usuarios
def abrir_abm_usuarios():
    abm = tk.Toplevel(root)
    abm.title("ABM de Usuarios")
    abm.geometry("500x300")

    tree = ttk.Treeview(abm, columns=("id", "nombre", "correo", "telefono", "direccion"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col.capitalize())
    tree.pack(fill=tk.BOTH, expand=True)

    def cargar_usuarios():
        for row in tree.get_children():
            tree.delete(row)
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()

    def agregar_usuario():
        nombre = simpledialog.askstring("Agregar Usuario", "Nombre:", parent=abm)
        if not nombre: return
        correo = simpledialog.askstring("Agregar Usuario", "Correo:", parent=abm)
        if not correo: return
        telefono = simpledialog.askstring("Agregar Usuario", "Teléfono:", parent=abm)
        if not telefono: return
        direccion = simpledialog.askstring("Agregar Usuario", "Dirección:", parent=abm)
        if not direccion: return
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre, correo, telefono, direccion) VALUES (%s, %s, %s, %s)",
                    (nombre, correo, telefono, direccion))
        conn.commit()
        cur.close()
        conn.close()
        cargar_usuarios()
        messagebox.showinfo("Éxito", "Usuario agregado correctamente.")

    def eliminar_usuario():
        selected = tree.selection()
        if selected:
            usuario_id = tree.item(selected[0])["values"][0]
            conn = mysql.connector.connect(**config)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM plantas WHERE id_usuario = %s", (usuario_id,))
            plantas_count = cur.fetchone()[0]
            if plantas_count > 0:
                if messagebox.askyesno("Advertencia", "Este usuario tiene plantas asociadas. ¿Deseas marcarlo como '--sin dueño--'?"):
                    cur.execute("UPDATE usuarios SET nombre='--sin dueño--', correo='--sin dueño--', telefono='--sin dueño--', direccion='--sin dueño--' WHERE id_usuario = %s", (usuario_id,))
            else:
                cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (usuario_id,))
            conn.commit()
            cur.close()
            conn.close()
            cargar_usuarios()
            messagebox.showinfo("Éxito", "Operación realizada correctamente.")

    def modificar_usuario():
        selected = tree.selection()
        if selected:
            usuario = tree.item(selected[0])["values"]
            usuario_id = usuario[0]
            nuevo_nombre = simpledialog.askstring("Modificar Usuario", "Nuevo nombre:", initialvalue=usuario[1], parent=abm)
            if nuevo_nombre is None: return
            nuevo_correo = simpledialog.askstring("Modificar Usuario", "Nuevo correo:", initialvalue=usuario[2], parent=abm)
            if nuevo_correo is None: return
            nuevo_telefono = simpledialog.askstring("Modificar Usuario", "Nuevo teléfono:", initialvalue=usuario[3], parent=abm)
            if nuevo_telefono is None: return
            nueva_direccion = simpledialog.askstring("Modificar Usuario", "Nueva dirección:", initialvalue=usuario[4], parent=abm)
            if nueva_direccion is None: return
            conn = mysql.connector.connect(**config)
            cur = conn.cursor()
            cur.execute("UPDATE usuarios SET nombre=%s, correo=%s, telefono=%s, direccion=%s WHERE id_usuario = %s",
                        (nuevo_nombre, nuevo_correo, nuevo_telefono, nueva_direccion, usuario_id))
            conn.commit()
            cur.close()
            conn.close()
            cargar_usuarios()
            messagebox.showinfo("Éxito", "Usuario modificado correctamente.")

    frm_botones = tk.Frame(abm)
    frm_botones.pack(pady=5)
    tk.Button(frm_botones, text="Agregar", command=agregar_usuario).pack(side=tk.LEFT, padx=5)
    tk.Button(frm_botones, text="Modificar", command=modificar_usuario).pack(side=tk.LEFT, padx=5)
    tk.Button(frm_botones, text="Eliminar", command=eliminar_usuario).pack(side=tk.LEFT, padx=5)

    cargar_usuarios()

# ABM Plantas
def abrir_abm_plantas():
    abm = tk.Toplevel(root)
    abm.title("ABM de Plantas")
    abm.geometry("500x300")

    tree = ttk.Treeview(abm, columns=("id_planta", "nombre", "especie", "id_usuario"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col.capitalize())
    tree.pack(fill=tk.BOTH, expand=True)

    def cargar():
        for row in tree.get_children():
            tree.delete(row)
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM plantas")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        cur.close()
        conn.close()

    def agregar():
        nombre = simpledialog.askstring("Agregar Planta", "Nombre:", parent=abm)
        if not nombre: return
        especie = simpledialog.askstring("Agregar Planta", "Especie:", parent=abm)
        if not especie: return

        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute("SELECT id_usuario, nombre FROM usuarios")
        usuarios = cur.fetchall()
        cur.close()
        conn.close()

        ventana_combo = tk.Toplevel(abm)
        ventana_combo.title("Seleccionar Usuario")
        tk.Label(ventana_combo, text="Seleccione usuario:").pack(pady=5)
        combo = ttk.Combobox(ventana_combo, values=[f"{u[0]} - {u[1]}" for u in usuarios], state="readonly")
        combo.pack(pady=5)

        def guardar():
            seleccionado = combo.get()
            if seleccionado:
                id_usuario = int(seleccionado.split(" - ")[0])
                conn = mysql.connector.connect(**config)
                cur = conn.cursor()
                cur.execute("INSERT INTO plantas (nombre, ubicacion, id_usuario) VALUES (%s, %s, %s)",
                            (nombre, especie, id_usuario))
                conn.commit()
                cur.close()
                conn.close()
                cargar()
                ventana_combo.destroy()
                messagebox.showinfo("Éxito", "Planta agregada.")

        tk.Button(ventana_combo, text="Guardar", command=guardar).pack(pady=5)

    def eliminar():
        selected = tree.selection()
        if selected:
            planta_id = tree.item(selected[0])["values"][0]
            conn = mysql.connector.connect(**config)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM sensores WHERE id_planta = %s", (planta_id,))
            sensores_count = cur.fetchone()[0]
            if sensores_count > 0:
                if messagebox.askyesno("Advertencia", "Esta planta tiene sensores. ¿Deseas marcarla como '--sin planta--'?"):
                    cur.execute("UPDATE plantas SET nombre='--sin planta--', ubicacion='--sin planta--' WHERE id_planta = %s", (planta_id,))
            else:
                cur.execute("DELETE FROM plantas WHERE id_planta = %s", (planta_id,))
            conn.commit()
            cur.close()
            conn.close()
            cargar()
            messagebox.showinfo("Éxito", "Operación realizada.")

    def modificar():
        selected = tree.selection()
        if selected:
            datos = tree.item(selected[0])["values"]
            planta_id = datos[0]
            nuevo_nombre = simpledialog.askstring("Modificar Planta", "Nuevo nombre:", initialvalue=datos[1], parent=abm)
            nueva_especie = simpledialog.askstring("Modificar Planta", "Nueva especie:", initialvalue=datos[2], parent=abm)

            conn = mysql.connector.connect(**config)
            cur = conn.cursor()
            cur.execute("SELECT id_usuario, nombre FROM usuarios")
            usuarios = cur.fetchall()
            cur.close()
            conn.close()

            ventana_combo = tk.Toplevel(abm)
            ventana_combo.title("Seleccionar Usuario")
            tk.Label(ventana_combo, text="Seleccione nuevo usuario:").pack()
            combo = ttk.Combobox(ventana_combo, values=[f"{u[0]} - {u[1]}" for u in usuarios], state="readonly")
            combo.pack()

            def actualizar_usuario():
                selected_user = combo.get()
                if selected_user:
                    id_usuario = int(selected_user.split(" - ")[0])
                    conn = mysql.connector.connect(**config)
                    cur = conn.cursor()
                    cur.execute("UPDATE plantas SET nombre=%s, ubicacion=%s, id_usuario=%s WHERE id_planta=%s",
                                (nuevo_nombre, nueva_especie, id_usuario, planta_id))
                    conn.commit()
                    cur.close()
                    conn.close()
                    ventana_combo.destroy()
                    cargar()
                    messagebox.showinfo("Éxito", "Planta modificada.")

            tk.Button(ventana_combo, text="Guardar", command=actualizar_usuario).pack()

    frm_botones = tk.Frame(abm)
    frm_botones.pack(pady=5)
    tk.Button(frm_botones, text="Agregar", command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(frm_botones, text="Modificar", command=modificar).pack(side=tk.LEFT, padx=5)
    tk.Button(frm_botones, text="Eliminar", command=eliminar).pack(side=tk.LEFT, padx=5)

    cargar()

# Gráficas
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

def actualizar(frame):
    datos = obtener_datos()
    if not datos:
        return
    horas = [row[0] for row in datos]
    temperatura = [row[1] for row in datos]
    humedad = [row[2] for row in datos]
    nivel_agua = [row[3] for row in datos]
    color_led = [row[4] for row in datos]

    ax1.clear()
    ax1.plot(horas, temperatura, label='Temperatura (°C)', color='red')
    ax1.plot(horas, humedad, label='Humedad (%)', color='blue')
    ax1.set_ylabel('Temp / Humedad')
    ax1.legend(loc='upper left')
    ax1.set_title('Sensores en Tiempo Real')

    ax2.clear()
    ax2.plot(horas, nivel_agua, label='Nivel Agua', color='green')
    ax2.set_ylabel('Nivel Agua')
    ax2.legend(loc='upper left')

    ax3.clear()
    for i in range(len(horas)):
        ax3.plot(horas[i], color_led[i], 'o', color=led_colores.get(color_led[i], 'black'))
    ax3.set_ylim(0.5, 3.5)
    ax3.set_ylabel('LED')
    ax3.set_yticks([1, 2, 3])
    ax3.set_yticklabels(['Verde', 'Naranja', 'Rojo'])
    ax3.set_title('Estado del LED (Color)')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()
    plt.tight_layout()

def mostrar_grafica():
    ani = FuncAnimation(fig, actualizar, interval=5000, cache_frame_data=False)
    plt.show()

# Botones
tk.Button(root, text="Mostrar Gráficas", command=mostrar_grafica).pack(pady=10)
tk.Button(root, text="ABM Usuarios", command=abrir_abm_usuarios).pack(pady=10)
tk.Button(root, text="ABM Plantas", command=abrir_abm_plantas).pack(pady=10)

root.mainloop()

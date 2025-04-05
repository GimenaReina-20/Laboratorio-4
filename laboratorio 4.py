    def read(self, muestras):
        datos = np.zeros((muestras,), dtype=np.float64)
        leidas = daqf.int32()
        self.ReadAnalogF64(muestras, 10.0, daqc.DAQmx_Val_GroupByChannel, datos, muestras, daqf.byref(leidas), None)
        return datos

def capturar():
    global capturando, data
    data = []
    daq = DAQ()
    daq.StartTask()
    while capturando:
        bloque = daq.read(100)
        data.extend(bloque)
        actualizar_grafica(data)
    daq.StopTask()
    daq.ClearTask()

def actualizar_grafica(datos):
    if not datos:
        return
    datos_filtrados = filtrar_emg(np.array(datos), fs)
    datos_suavizados = suavizar_senal(datos_filtrados)
    t = np.linspace(0, len(datos_suavizados) / fs, len(datos_suavizados))
    line.set_data(t, datos_suavizados)
    ax.set_xlim(0, max(1, t[-1]))
    ax.set_ylim(min(datos_suavizados) - 0.1, max(datos_suavizados) + 0.1)
    canvas.draw()

def guardar_datos():
    global data
    if not data:
        messagebox.showwarning("Advertencia", "No hay datos capturados.")
        return
    t = np.linspace(0, len(data) / fs, len(data))
    with open(archivo, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Tiempo(s)", "EMG(V)"])
        for i in range(len(data)):
            writer.writerow([round(t[i], 4), round(data[i], 6)])
    messagebox.showinfo("Guardado", f"Datos guardados como {archivo}")

def iniciar():
    global capturando
    capturando = True
    hilo = threading.Thread(target=capturar)
    hilo.start()

def detener():
    global capturando
    capturando = False

# Interfaz Tkinter
ventana = tk.Tk()
ventana.title("Señal EMG - Captura y Análisis")
ventana.geometry("800x600")

fig, ax = plt.subplots(figsize=(7, 4))
line, = ax.plot([], [])
ax.set_title("Señal EMG en Tiempo Real")
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Voltaje (V)")
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().pack()

frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=20)

btn_iniciar = tk.Button(frame_botones, text="Iniciar Captura", command=iniciar)
btn_iniciar.grid(row=0, column=0, padx=10)

btn_detener = tk.Button(frame_botones, text="Detener y Guardar", command=lambda:[detener(), guardar_datos()])
btn_detener.grid(row=0, column=1, padx=10)

ventana.mainloop()

# Laboratorio 4: Señales electromiogtráficas EMG

## Introducción:
El electromiograma (EMG) es una herramienta fundamental para el estudio de la actividad muscular, ya que permite registrar la señal eléctrica generada por las contracciones musculares. En esta práctica, se obtuvo la señal EMG del músculo de la pantorrilla para analizar la fatiga muscular a partir del procesamiento de sus picos, los cuales corresponden a contracciones. Se aplicaron en cada pico para su análisis detallado, utilizando técnicas de filtrado y espectro de frecuencia en Python. Este estudio permite comprender la evolución de la señal durante el esfuerzo muscular y la contracción de un músculo que pasa por la fase de fatiga.

## Paso a paso:
1. Colocación de electrodos y conexión de DAQ.
2. Adquisición de la señal EMG.
3. Procesamiento de la señal:
  3.1. Filtrado de señal.
  3.2. Detección de picos.
  3.3. Aplicaión de ventana.
4. Análisis de fatiga.
5. Interpretación y almacenamiento.

## Programación y datos:
### 1. Captura de la señal emg:
Se desarrolló una clase que permite leer datos analógicos desde un dispositivo DAQ. La función read lee bloques de muestras en punto flotante:

def read(self, muestras):
    datos = np.zeros((muestras,), dtype=np.float64)
    leidas = daqf.int32()
    self.ReadAnalogF64(muestras, 10.0, daqc.DAQmx_Val_GroupByChannel, datos, muestras, daqf.byref(leidas), None)
    return datos

La función capturar() ejecuta un bucle de lectura en un hilo separado para no congelar la interfaz gráfica. Cada bloque leído se filtra, suaviza y grafica en tiempo real:

def capturar():
    global capturando, data
    data = []
    daq = DAQ()
    daq.StartTask()
    while capturando:
        bloque = daq.read(100)
        data.extend(bloque)
        actualizar_grafica(data)

Se utilizó Tkinter y Matplotlib para crear una interfaz donde el usuario puede iniciar/detener la captura y observar la señal en tiempo real.

btn_iniciar = tk.Button(frame_botones, text="Iniciar Captura", command=iniciar)
btn_detener = tk.Button(frame_botones, text="Detener y Guardar", command=lambda:[detener(), guardar_datos()])

### 2. Procesamiento de la señal EMG:
Una vez finalizada la captura, la señal se guarda en un archivo CSV y se procesa mediante:
- Filtro pasa banda (20–450 Hz) para eliminar ruido.
- Cálculo de la envolvente con transformada de Hilbert.
- Cálculo de frecuencia mediana por ventanas.

def filtro_pasa_banda(senal, fs, lowcut, highcut, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    return filtfilt(b, a, senal)

### 3. Visualización de resultados:
![Figura 1 lab 4](https://github.com/user-attachments/assets/46e6fe1b-a6f4-494b-b132-5a42c608a6d4)
![Figura 2 lab 4](https://github.com/user-attachments/assets/24b946fa-fd1a-477e-9617-6f4d83704b51)
![Figura 3 lab 4](https://github.com/user-attachments/assets/411c39ce-6e9c-47e0-8a05-28d81a33e72f)
![Figura 5 lab 4](https://github.com/user-attachments/assets/616dbe39-b505-462b-9905-424aff89ed65)
<img width="481" alt="Figura 6 lab 4" src="https://github.com/user-attachments/assets/87deb2be-c452-4f98-95f8-ccb06685cd02" />

### 4. Análisis de frecuencia mediana: 
Se definieron ventanas manuales donde se identifican contracciones musculares. Para cada ventana, se calculó la frecuencia mediana del espectro de potencia, útil para detectar fatiga muscular.

f_mediana = freqs[np.where(potencia_acumulada >= potencia_total / 2)[0][0]]

### 5. Prueba de hipótesis: fatiga muscular:
Se dividieron las contracciones en dos grupos (inicio y fin del experimento) y se aplicó una prueba t de Student para evaluar si hay una diferencia significativa en la frecuencia mediana (indicador de fatiga):

t_stat, p_value = ttest_ind(grupo1, grupo2)

Si el valor p < 0.05 → fatiga detectada.


## Ventanas:


## Análisis de resultados:


## Conclusiones:


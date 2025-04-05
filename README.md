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
La clase DAQ se conecta a un sistema de adquisición de datos (DAQ) que permite leer datos analógicos. La función read() extrae muestras en tiempo real:

def read(self, muestras):
    datos = np.zeros((muestras,), dtype=np.float64)
    leidas = daqf.int32()
    self.ReadAnalogF64(muestras, 10.0, daqc.DAQmx_Val_GroupByChannel, datos, muestras, daqf.byref(leidas), None)
    return datos

Este bloque configura el búfer de lectura y adquiere los datos directamente del canal del DAQ, garantizando precisión en la temporalidad de los datos.

Se creó un hilo separado con la función capturar() que mantiene el bucle de lectura mientras se activa la variable capturando. Se filtran y grafican los datos en tiempo real:

def capturar():
    global capturando, data
    data = []
    daq = DAQ()
    daq.StartTask()
    while capturando:
        bloque = daq.read(100)
        data.extend(bloque)
        actualizar_grafica(data)

La interfaz fue desarrollada con Tkinter. Incluye botones para iniciar y detener la adquisición, y visualiza la señal con Matplotlib embebido:

btn_iniciar = tk.Button(frame_botones, text="Iniciar Captura", command=iniciar)
btn_detener = tk.Button(frame_botones, text="Detener y Guardar", command=lambda:[detener(), guardar_datos()])

### 2. Procesamiento de la señal EMG:
La señal EMG fue procesada con un filtro Butterworth de orden 4, que permite eliminar componentes no deseadas fuera del rango 20–450 Hz (frecuencias musculares relevantes):

def filtro_pasa_banda(senal, fs, lowcut=20, highcut=450, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    return filtfilt(b, a, senal)

![Figura 1 lab 4](https://github.com/user-attachments/assets/46e6fe1b-a6f4-494b-b132-5a42c608a6d4)
![Figura 2 lab 4](https://github.com/user-attachments/assets/24b946fa-fd1a-477e-9617-6f4d83704b51)

La envolvente se obtuvo usando la transformada de Hilbert. Esta técnica permite observar la amplitud instantánea de la señal y es útil para detectar momentos de contracción muscular:

envolvente = np.abs(hilbert(emg_filtrada))

![Figura 3 lab 4](https://github.com/user-attachments/assets/411c39ce-6e9c-47e0-8a05-28d81a33e72f)

### 3. Análisis de frecuencia mediana por ventanas:
Se seleccionaron manualmente ventanas de tiempo donde se observaron contracciones musculares. Para cada una, se aplicó transformada rápida de Fourier (FFT), y se calculó la frecuencia mediana:

f_mediana = freqs[np.where(potencia_acumulada >= potencia_total / 2)[0][0]]

La frecuencia mediana representa el punto donde la energía espectral se divide en dos partes iguales y sirve como indicador de fatiga muscular.

### 4. Prueba de hipótesis: 
Para evaluar si hay fatiga, se dividieron las ventanas en dos grupos (inicio vs. final) y se aplicó una prueba t de Student para muestras independientes:

f_mediana = freqs[np.where(potencia_acumulada >= potencia_total / 2)[0][0]]

Si el valor p < 0.05, se considera que la diferencia es significativa, lo cual puede indicar fatiga muscular debido a la disminución de frecuencia mediana.

## Análisis de resultados:
<img width="481" alt="Figura 6 lab 4" src="https://github.com/user-attachments/assets/8496ba5f-0058-44eb-8f7a-c03050cd79e2" />

### 1. Frecuencia de Muestreo
Se estimó una frecuencia de muestreo de 1000 Hz, lo cual es apropiado para señales EMG, ya que permite capturar con fidelidad sus componentes de alta frecuencia (hasta 500 Hz según literatura).

### 2. Exportación de Datos
Las señales fueron exportadas correctamente en tres archivos:
- senal_original.csv: señal cruda adquirida del sistema DAQ.
- senal_filtrada.csv: señal luego del filtrado pasa banda (20–450 Hz).
- envolvente_hilbert.csv: energía instantánea de la señal, útil para segmentación.
### Observaciones
- No se observa una tendencia clara decreciente en la frecuencia mediana a lo largo del tiempo.
- Algunas ventanas intermedias (como la 2 y la 6) presentan frecuencias más altas que otras.
- Esto sugiere que no hubo una acumulación sistemática de fatiga a lo largo de la prueba.

### 3. Prueba de hipótesis
Para comprobar si existía una diferencia significativa en la frecuencia mediana entre la primera mitad (ventanas 1–5) y la segunda mitad (ventanas 6–10), se aplicó una prueba t para muestras independientes:
- T-statistic: −0.0072
- P-value: 0.9944
### Observaciones
- Un p-value cercano a 1 indica que no hay diferencias estadísticamente significativas entre los dos grupos.
- Por tanto, no se detectó evidencia clara de fatiga muscular durante el experimento.
- Esto puede deberse a una recuperación suficiente entre contracciones o a que el esfuerzo no fue lo suficientemente prolongado para inducir fatiga.

## Conclusiones:
Los resultados indican que el protocolo de contracción muscular utilizado no generó signos evidentes de fatiga. A pesar de que se aplicó una metodología robusta de procesamiento y análisis de señales, la estabilidad de la frecuencia mediana sugiere que el músculo no entró en un estado de fatiga medible a nivel espectral.

## Referencias:
- C. J. De Luca, “The use of surface electromyography in biomechanics,” Journal of Applied Biomechanics, vol. 13, no. 2, pp. 135–163, May 1997, doi: 10.1123/jab.13.2.135.
- D. M. Freeman, “Fast arithmetic and pairing evaluation on genus 2 curves,” ResearchGate, Dec. 2005, [Online]. Available: https://www.researchgate.net/publication/228684792_Fast_arithmetic_and_pairing_evaluation_on_genus_2_curves
- A. Phinyomark, P. Phukpattaranont, and C. Limsakul, “Feature reduction and selection for EMG signal classification,” Expert Systems With Applications, vol. 39, no. 8, pp. 7420–7431, Jan. 2012, doi: 10.1016/j.eswa.2012.01.102.
- B. Maton, G. Thiney, A. Ouchène, P. Flaud, and P. Barthelemy, “Intramuscular pressure and surface EMG in voluntary ankle dorsal flexion: Influence of elastic compressive stockings,” Journal of Electromyography and Kinesiology, vol. 16, no. 3, pp. 291–302, Aug. 2005, doi: 10.1016/j.jelekin.2005.07.006.

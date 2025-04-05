import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, windows, find_peaks
from scipy.fft import fft, fftfreq
from scipy.stats import ttest_ind
from scipy.signal import butter, filtfilt, hilbert, windows

ruta = r"C:\Users\ASUS\Documents\PRIMER SEMESTRE\captura señal emg.csv"

df = pd.read_csv(ruta)

# === Cargar datos ===
df = pd.read_csv(ruta)
tiempo = df.iloc[:, 0].values
emg = df.iloc[:, 1].values
fs = int(1 / (tiempo[1] - tiempo[0]))
print(f"\nFrecuencia de muestreo estimada: {fs} Hz")

# === Filtro pasa banda (20-450 Hz) ===
def filtro_pasa_banda(senal, fs, lowcut, highcut, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    return filtfilt(b, a, senal)

emg_filtrada = filtro_pasa_banda(emg, fs, 20, 450)

# === Calcular envolvente de Hilbert ===
envolvente = np.abs(hilbert(emg_filtrada))

# === Exportar CSV de señales ===
df_original = pd.DataFrame({'Tiempo [s]': tiempo, 'EMG Original': emg})
df_filtrada = pd.DataFrame({'Tiempo [s]': tiempo, 'EMG Filtrada': emg_filtrada})
df_envolvente = pd.DataFrame({'Tiempo [s]': tiempo, 'Envolvente Hilbert': envolvente})

df_original.to_csv("senal_original.csv", index=False)
df_filtrada.to_csv("senal_filtrada.csv", index=False)
df_envolvente.to_csv("envolvente_hilbert.csv", index=False)

print("\n✅ Señales exportadas:")
print("→ senal_original.csv")
print("→ senal_filtrada.csv")
print("→ envolvente_hilbert.csv")

# === Graficar señal original y filtrada ===
# === Graficar señal original ===
plt.figure()
plt.plot(tiempo, emg, label="Señal Original", color='skyblue')
plt.title("Señal EMG Original")
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

# === Graficar señal filtrada ===
plt.figure()
plt.plot(tiempo, emg_filtrada, label="Señal Filtrada", color='orange')
plt.title("Señal EMG Filtrada (20-450 Hz)")
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

# === Graficar envolvente de Hilbert ===
plt.figure()
plt.plot(tiempo, envolvente, label="Envolvente de Hilbert", color='green')
plt.title("Envolvente de la Señal EMG")
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()


# === Definir ventanas de contracciones manuales ===
ventanas = [
    {"inicio": 0.461, "fin": 0.592},
    {"inicio": 1.369, "fin": 1.381},
    {"inicio": 1.388, "fin": 2.749},
    {"inicio": 3.483, "fin": 4.574},
    {"inicio": 5.461, "fin": 6.419},
    {"inicio": 6.428, "fin": 6.441},
    {"inicio": 7.296, "fin": 8.393},
    {"inicio": 9.193, "fin": 10.302},
    {"inicio": 11.105, "fin": 12.199},
    {"inicio": 13.344, "fin": 14.624},
]

# === Cálculo de frecuencia mediana por ventana ===
frecuencias_medianas = []

for idx, ventana in enumerate(ventanas, start=1):
    idx_ini = int(ventana["inicio"] * fs)
    idx_fin = int(ventana["fin"] * fs)
    segmento = emg_filtrada[idx_ini:idx_fin]

    ventana_hamming = np.hamming(len(segmento))
    segmento_vent = segmento * ventana_hamming

    fft_segmento = np.abs(fft(segmento_vent))
    freqs = fftfreq(len(segmento_vent), d=1/fs)
    fft_segmento = fft_segmento[:len(fft_segmento)//2]
    freqs = freqs[:len(freqs)//2]

    potencia_total = np.sum(fft_segmento)
    potencia_acumulada = np.cumsum(fft_segmento)
    f_mediana = freqs[np.where(potencia_acumulada >= potencia_total / 2)[0][0]]
    frecuencias_medianas.append(f_mediana)

    print(f"Ventana {idx}: Frecuencia mediana = {f_mediana:.2f} Hz")

# === Gráfica de frecuencia mediana por ventana ===
plt.figure()
plt.plot(range(1, len(frecuencias_medianas)+1), frecuencias_medianas, marker='o', color='green')
plt.title("Frecuencia Mediana por Ventana Manual")
plt.xlabel("Ventana")
plt.ylabel("Frecuencia Mediana [Hz]")
plt.grid()
plt.tight_layout()
plt.show()

# === Prueba de hipótesis (fatiga muscular) ===
mitad = len(frecuencias_medianas) // 2
grupo1 = frecuencias_medianas[:mitad]
grupo2 = frecuencias_medianas[mitad:]

t_stat, p_value = ttest_ind(grupo1, grupo2)

print("\n📊 Prueba de hipótesis sobre la frecuencia mediana:")
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")
if p_value < 0.10:
    print("✅ Diferencia significativa en frecuencia mediana (fatiga detectada).")
else:
    print("❌ No se detectó diferencia significativa (sin evidencia clara de fatiga).")

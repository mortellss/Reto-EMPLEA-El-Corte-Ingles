from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent

PASOS = [
    ROOT / "FASE_1_modelo" / "importar_datos.py",
    ROOT / "FASE_1_modelo" / "entrenamiento_prophet.py",
    ROOT / "FASE_2 _programacion_lineal" / "optimizacion_FINAL.py",
    ROOT / "FASE_3_calendarizacion" / "calendarizacion.py",
]


def main():
    for numero, paso in enumerate(PASOS, start=1):
        print(f"\n[{numero}/{len(PASOS)}] Ejecutando: {paso.name}")
        subprocess.run([sys.executable, str(paso)], cwd=paso.parent, check=True)

    print("\nPipeline completado correctamente.")


if __name__ == "__main__":
    main()
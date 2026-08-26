import subprocess
import sys

# la ruta del script principal
ruta_cli = "src/app_operator.py"

# aca van los casos de prueba, cada uno con sus argumentos
casos = [
    ["AWS", "GCP", "-c", "cluster-us-east-01", "-t", "3.0"],   # caso normal
    ["AWS", "Azure", "-c", "cluster-us-east-01", "-t", "0.1"], # timeout muy bajo
    ["AWS", "-c", "cluster-mal-escrito", "-t", "3.0"],         # cluster invalido
    ["AWS", "-c", "cluster-us-east-01", "-t", "9.5"],          # timeout fuera de rango
    ["AWS", "Azure", "GCP", "-c", "cluster-us-west-02", "-t", "1.5", "--chaos"],  # modo caos
]

print("="*50)
print("INICIANDO SIMULACION DE CAOS")
print("="*50)

for i, args in enumerate(casos, 1):
    comando = [sys.executable, ruta_cli] + args
    print("\nPrueba", i, ":", " ".join(comando))
    
    # ejecutar el comando y esperar
    proceso = subprocess.run(comando, capture_output=True, text=True)
    
    if proceso.returncode == 0:
        print("   Salió bien (codigo 0)")
    else:
        print("   Salió mal (codigo", proceso.returncode, ")")
        # mostramos solo un pedacito del error para no llenar la pantalla
        if proceso.stderr:
            print("   Error:", proceso.stderr[:150])

print("\nSimulacion de caos terminada.")
print("Revisa los archivos triton_services.log y los .gz que se generaron.")
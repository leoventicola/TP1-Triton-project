import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


# Ruta del proyecto y del script principal
directorio_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_cli = os.path.join(directorio_proyecto, "src", "app_operator.py")


# Casos de prueba
casos = [
    {
        "nombre": "Operacion normal",
        "args": [
            "AWS", "GCP",
            "-c", "cluster-us-east-01",
            "-t", "3.0"
        ],
        "codigo_esperado": 0
    },
    {
        "nombre": "Timeout muy bajo",
        "args": [
            "AWS", "Azure",
            "-c", "cluster-us-east-01",
            "-t", "0.1"
        ],
        "codigo_esperado": 0
    },
    {
        "nombre": "Cluster invalido",
        "args": [
            "AWS",
            "-c", "cluster-mal-escrito",
            "-t", "3.0"
        ],
        "codigo_esperado": 2
    },
    {
        "nombre": "Timeout fuera de rango",
        "args": [
            "AWS",
            "-c", "cluster-us-east-01",
            "-t", "9.5"
        ],
        "codigo_esperado": 2
    },
    {
        "nombre": "Modo caos",
        "args": [
            "AWS", "Azure", "GCP",
            "-c", "cluster-us-west-02",
            "-t", "1.5",
            "--chaos"
        ],
        "codigo_esperado": 0
    }
]


def ejecutar_prueba(caso):
    """
    Ejecuta una prueba del CLI y devuelve su resultado.
    """
    comando = [sys.executable, ruta_cli] + caso["args"]

    try:
        proceso = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            cwd=directorio_proyecto
        )

        return {
            "nombre": caso["nombre"],
            "codigo_esperado": caso["codigo_esperado"],
            "returncode": proceso.returncode,
            "stdout": proceso.stdout,
            "stderr": proceso.stderr
        }

    except OSError as error:
        return {
            "nombre": caso["nombre"],
            "codigo_esperado": caso["codigo_esperado"],
            "returncode": None,
            "stdout": "",
            "stderr": str(error)
        }


print("=" * 50)
print("INICIANDO SIMULACION DE CAOS")
print("=" * 50)


resultados = []


# Ejecutar las pruebas de forma concurrente
with ThreadPoolExecutor(max_workers=len(casos)) as executor:

    trabajos = [
        executor.submit(ejecutar_prueba, caso)
        for caso in casos
    ]

    for trabajo in as_completed(trabajos):
        resultado = trabajo.result()
        resultados.append(resultado)

        print("\nPrueba:", resultado["nombre"])
        print("   Codigo esperado:", resultado["codigo_esperado"])
        print("   Codigo obtenido:", resultado["returncode"])

        # Comparar el resultado real con el esperado
        if resultado["returncode"] == resultado["codigo_esperado"]:
            print("   Resultado: OK")
        else:
            print("   Resultado: ERROR")

            if resultado["stderr"]:
                print(
                    "   Error:",
                    resultado["stderr"][:150].replace("\n", " ")
                )


# Resumen final
total_pruebas = len(resultados)

pruebas_ok = sum(
    1
    for resultado in resultados
    if resultado["returncode"] == resultado["codigo_esperado"]
)

pruebas_error = total_pruebas - pruebas_ok


print("\n" + "=" * 50)
print("RESUMEN")
print("=" * 50)
print("Pruebas ejecutadas:", total_pruebas)
print("Pruebas correctas:", pruebas_ok)
print("Pruebas con errores:", pruebas_error)

print("\nRevisa los archivos triton_services.log y los backups .gz")
print("para comprobar la telemetria generada.")

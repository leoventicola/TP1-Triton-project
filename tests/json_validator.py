import json
import gzip
import os


# Archivos que puede haber generado el sistema
archivos = [
    "triton_services.log",
    "triton_services.log.1.gz",
    "triton_services.log.2.gz",
    "triton_services.log.3.gz",
]


print("=" * 50)
print("VALIDANDO LOGS")
print("=" * 50)


todo_bien = True
archivos_encontrados = 0
lineas_verificadas = 0
errores_encontrados = 0


for ruta in archivos:
    print("\nLeyendo:", ruta)

    # Verificar si el archivo existe antes de intentar abrirlo
    if not os.path.exists(ruta):
        print("   El archivo no existe")
        continue

    archivos_encontrados += 1

    # Abrir el archivo según sea normal o comprimido
    if ruta.endswith(".gz"):
        f = gzip.open(ruta, "rt", encoding="utf-8")
    else:
        f = open(ruta, "r", encoding="utf-8")

    lineas = f.readlines()
    f.close()

    if len(lineas) == 0:
        print("   El archivo esta vacio")
        continue

    for num in range(len(lineas)):
        linea = lineas[num].strip()

        if not linea:
            continue

        lineas_verificadas += 1

        try:
            datos = json.loads(linea)

        except json.JSONDecodeError:
            print("   Linea", num + 1, ": no es JSON valido")
            todo_bien = False
            errores_encontrados += 1
            continue

        # Verificar timestamp
        ts = datos.get("timestamp")

        if ts is None:
            print("   Linea", num + 1, ": falta timestamp")
            todo_bien = False
            errores_encontrados += 1

        elif not ts.endswith("Z"):
            print(
                "   Linea", num + 1,
                ": timestamp no es UTC (debe terminar en Z):", ts
            )
            todo_bien = False
            errores_encontrados += 1

        # Si hay exception_tree, revisar class, message y notes
        if "exception_tree" in datos:
            arbol = datos["exception_tree"]

            if "class" not in arbol or "message" not in arbol:
                print(
                    "   Linea", num + 1,
                    ": exception_tree incompleto "
                    "(falta class o message)"
                )
                todo_bien = False
                errores_encontrados += 1

            else:
                notas = arbol.get("notes", [])

                if not notas:
                    print(
                        "   Linea", num + 1,
                        ": exception_tree no tiene notes "
                        "(capaz falta add_note)"
                    )
                    todo_bien = False
                    errores_encontrados += 1

                else:
                    print(
                        "   Linea", num + 1,
                        ": exception_tree ok con notes"
                    )


print("\n" + "=" * 50)
print("RESUMEN")
print("=" * 50)
print("Lineas verificadas:", lineas_verificadas)
print("Errores encontrados:", errores_encontrados)


# No se puede decir que los logs son validos si no se encontro ninguno
if archivos_encontrados == 0:
    print("Resultado: NO SE ENCONTRARON ARCHIVOS DE LOG")

elif todo_bien:
    print("Resultado: TODOS LOS LOGS SON VALIDOS")

else:
    print("Resultado: HAY LOGS CON ERRORES")

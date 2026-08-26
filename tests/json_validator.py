import json
import gzip

# archivos que puede haber generado el sistema
archivos = [
    "triton_services.log",
    "triton_services.log.1.gz",
    "triton_services.log.2.gz",
    "triton_services.log.3.gz",
]

print("="*50)
print("VALIDANDO LOGS")
print("="*50)

todo_bien = True

for ruta in archivos:
    print("\nLeyendo:", ruta)
    
    # abrir el archivo (si es .gz uso gzip, sino normal)
    if ruta.endswith(".gz"):
        f = gzip.open(ruta, 'rt', encoding='utf-8')
    else:
        f = open(ruta, 'r', encoding='utf-8')
    
    lineas = f.readlines()
    f.close()
    
    if len(lineas) == 0:
        print("   El archivo esta vacio")
        continue
    
    for num in range(len(lineas)):
        linea = lineas[num].strip()
        if not linea:
            continue
        
        try:
            datos = json.loads(linea)
        except:
            print("   Linea", num+1, ": no es JSON valido")
            todo_bien = False
            continue
        
        # verificar timestamp
        ts = datos.get("timestamp")
        if ts is None:
            print("   Linea", num+1, ": falta timestamp")
            todo_bien = False
        elif not ts.endswith("Z"):
            print("   Linea", num+1, ": timestamp no es UTC (debe terminar en Z):", ts)
            todo_bien = False
        
        # si hay exception_tree, revisar que tenga class, message y notes
        if "exception_tree" in datos:
            arbol = datos["exception_tree"]
            if "class" not in arbol or "message" not in arbol:
                print("   Linea", num+1, ": exception_tree incompleto (falta class o message)")
                todo_bien = False
            else:
                notas = arbol.get("notes", [])
                if not notas:
                    print("   Linea", num+1, ": exception_tree no tiene notes (capaz falta add_note)")
                    todo_bien = False
                else:
                    print("   Linea", num+1, ": exception_tree ok con notes")

if todo_bien:
    print("\nTodos los logs estan bien")
else:
    print("\nHay logs con errores")
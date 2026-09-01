## Entorno de desarrollo

Antes de comenzar, seguí las instrucciones de instalación
y configuración indicadas en el [README.md](README.md).

Una vez configurado el entorno, podés ejecutar las pruebas y herramientas
de calidad descritas a continuación.

## Tests

Instalar el paquete `trinton_telemetry` (Opcional para realizar tests)

Para ejecutar los tests ubicados en `tests/`, instalar el paquete en modo editable:
      
```bash
pip install -e .
```

[4. Ejecutar el proyecto]: #

## Configuración VS CODE

Se recomienda utilizar Visual Studio Code como editor y seleccionar el intérprete de Python correspondiente al entorno virtual del proyecto.

1. Abrir la **Paleta de comandos**

      **Ver → Paleta de comandos**.

2. Seleccionar:

        >Python: Select Interpreter

3. Seleccionar el intérprete del entorno virtual:
    
    - Windows:
        ```bash
        .venv\Scripts\python.exe
        ```

    - Linux/macOS:

        ```bash
        .venv/bin/python
        ```
  Aclaración: El repositorio incluye un archivo settings.json con la configuración recomendada para el entorno de desarrollo en VS Code.
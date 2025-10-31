
### 1\. Abrir el Proyecto en Visual Studio Code

1.  Abre **Visual Studio Code**.
2.  Ve a `Archivo > Abrir Carpeta...` (o `File > Open Folder...`).
3.  Navega hasta la carpeta `gestor_ventas` (la que contiene `app.py`) y selecciónala.

### 2\. Configurar el Entorno Virtual (venv)

Es crucial crear un entorno virtual para aislar las dependencias de tu proyecto.

1.  **Abre la Terminal Integrada de VS Code:**
    * Ve a `Terminal > Nueva Terminal` (o `Terminal > New Terminal`) en el menú superior.
    * Verás que la terminal se abre automáticamente en la carpeta `gestor_ventas`.

2.  **Crea el Entorno Virtual:** Ejecuta el siguiente comando para crear la carpeta `.venv` con tu entorno virtual:
    ```bash
    python -m venv .venv
    ```

### 3\. Activar el Entorno Virtual

Ahora, activa el entorno virtual que acabas de crear. El comando varía según tu sistema operativo:

* **En Windows (usando PowerShell en la terminal de VS Code):**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```
* **En Windows (usando Command Prompt - `cmd.exe`):**
    ```cmd
    .venv\Scripts\activate.bat
    ```

### 4\. Instalar las Dependencias del Proyecto

Con el entorno virtual activado, instala todas las librerías necesarias listadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5\. Ejecutar la Aplicación Flask:
          python app.py

# Proyecto Urban Routes - Pruebas Automatizadas UI

## Descripción del Proyecto
Este proyecto contiene un conjunto de pruebas de automatización End-to-End (E2E) para la aplicación web **Urban Routes**. La suite de pruebas cubre todo el flujo de pedido de un taxi, garantizando la correcta interacción con componentes como:
- Configuración de la ruta (origen y destino).
- Selección de la tarifa Comfort.
- Confirmación de número telefónico mediante código SMS interceptado de la red.
- Enlace de tarjeta de crédito.
- Inclusión de comentarios para el conductor.
- Selección de requisitos adicionales (manta, pañuelos y helados).
- Confirmación de la búsqueda del taxi y asignación del conductor.

## Tecnologías y Tecnicas Utilizadas
- **Lenguaje:** Python 3.x
- **Framework de Pruebas:** Pytest
- **Herramienta de Automatización:** Selenium WebDriver
- **Patrón de Diseño:** Page Object Model (POM)
- **Otras Librerías:** `selenium.webdriver.common.by`, `selenium.webdriver.support.ui` (WebDriverWait)

## Instrucciones de Ejecución

1. **Clonar el repositorio y abrir en PyCharm:**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd qa-project-Urban-Routes-es

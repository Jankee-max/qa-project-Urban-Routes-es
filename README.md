Este proyecto contiene un conjunto de pruebas de automatización End-to-End (E2E) para la aplicación web Urban Routes. La suite de pruebas cubre todo el flujo de pedido de un taxi, garantizando la correcta interacción con componentes como:

Configuración de la ruta (origen y destino).
Selección de la tarifa Comfort.
Confirmación de número telefónico mediante código SMS interceptado de la red.
Enlace de tarjeta de crédito.
Inclusión de comentarios para el conductor.
Selección de requisitos adicionales (manta, pañuelos y helados).
Confirmación de la búsqueda del taxi y asignación del conductor.
Tecnologías y Técnicas Utilizadas
Lenguaje: Python 3.x
Framework de Pruebas: Pytest
Herramienta de Automatización: Selenium WebDriver
Patrón de Diseño: Page Object Model (POM) — la clase UrbanRoutesPage encapsula los localizadores y acciones sobre la interfaz, separada de la clase de pruebas TestUrbanRoutes
Esperas explícitas: WebDriverWait + expected_conditions para sincronizar con elementos dinámicos (modales, campos que aparecen tras una acción)
Interceptación de red: lectura de los logs de rendimiento del navegador (performance logs + Chrome DevTools Protocol) para obtener el código de confirmación telefónica sin intervención manual
Otras librerías: selenium.webdriver.common.by, selenium.webdriver.support.ui (WebDriverWait), selenium.webdriver.common.keys
Estructura del Proyecto
qa-project-Urban-Routes-es/
├── data.py     # URL del servidor y datos de prueba (direcciones, teléfono, tarjeta, mensaje)
├── main.py     # UrbanRoutesPage (Page Object) + retrieve_phone_code() + TestUrbanRoutes (pruebas)
└── README.md
Instrucciones de Ejecución
1. Clonar el repositorio y abrirlo en PyCharm
git clone https://github.com/Jankee-max/qa-project-Urban-Routes-es
cd qa-project-Urban-Routes-es

En PyCharm: File → Open y selecciona la carpeta clonada, o usa Get from VCS pegando la URL del repositorio directamente.

2. Configurar el intérprete de Python

En PyCharm, si aparece el aviso "No Python interpreter configured", haz clic en Create a virtual environment para crear un entorno virtual (.venv) dentro del proyecto.

3. Instalar las dependencias

Desde la terminal integrada de PyCharm:

pip install selenium pytest
4. Configurar la URL del servidor

Abre el archivo data.py y reemplaza el valor de urban_routes_url por la URL de tu servidor de pruebas (la que te proporciona la plataforma), incluyendo el parámetro ?lng=es.

5. Verificar Google Chrome

Asegúrate de tener Google Chrome instalado. Selenium 4.6+ descarga y gestiona el driver de Chrome automáticamente, así que normalmente no necesitas instalar nada adicional.

6. Ejecutar las pruebas

Desde la terminal, dentro de la carpeta del proyecto:

pytest main.py -v

También puedes ejecutarlas desde PyCharm: clic derecho sobre main.py → Run pytest in main.py.

Casos de Prueba Cubiertos
test_set_route — Configuración de la dirección de origen y destino
test_select_comfort_rate — Selección de la tarifa Comfort
test_fill_phone_number — Llenado y verificación del número de teléfono, incluyendo la obtención automática del código SMS
test_add_credit_card — Registro de tarjeta de crédito (incluye manejo del enfoque del campo CVV para activar el botón de confirmación)
test_write_message_for_driver — Mensaje de texto para el conductor
test_order_blanket_and_tissues — Solicitud de manta y pañuelos
test_order_ice_cream — Solicitud de 2 helados
test_order_taxi_modal_appears — Aparición del modal de búsqueda de taxi
Notas
La función retrieve_phone_code() obtiene el código de confirmación leyendo el cuerpo de la respuesta de red (Network.getResponseBody) asociada a la petición api/v1/number?number=..., en lugar de extraerlo de la URL, ya que el código real viaja en el cuerpo de la respuesta del servidor.
El número de teléfono en data.py debe tener un formato válido para que la aplicación acepte la solicitud (por ejemplo, 9991234567).

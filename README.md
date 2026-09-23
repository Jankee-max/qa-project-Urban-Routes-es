# qa-project-Urban-Routes-es

## Descripción del proyecto

Suite de pruebas automatizadas para la aplicación web **Urban Routes**, un
simulador de pedido de taxis (estilo Yandex.Taxi). El proyecto valida el
flujo completo de un usuario al pedir un viaje: configuración de la ruta,
selección de tarifa, verificación de teléfono, registro de tarjeta de
crédito, mensaje para el conductor, solicitud de manta/pañuelos y helados,
y la aparición del modal de búsqueda de conductor.

## Tecnologías y técnicas utilizadas

- **Python 3**
- **Selenium WebDriver** — automatización de la interfaz web
- **pytest** — framework de pruebas y aserciones
- **Patrón Page Object Model (POM)** — clase `UrbanRoutesPage` que encapsula
  localizadores y acciones, separada de la clase de pruebas `TestUrbanRoutes`
- **Esperas explícitas** (`WebDriverWait` + `expected_conditions`) para
  sincronizar con elementos dinámicos (modales, campos que aparecen tras una
  acción)
- Interceptación de código de verificación telefónica mediante la función
  `retrieve_phone_code()` incluida en el repositorio

## Estructura del proyecto

```
qa-project-Urban-Routes-es/
├── data.py        # URL del servidor y datos de prueba (direcciones, teléfono, tarjeta)
├── helpers.py      # Función retrieve_phone_code() para obtener el código SMS
├── main.py        # UrbanRoutesPage (Page Object) + TestUrbanRoutes (pruebas)
└── README.md
```

## Cómo ejecutar las pruebas

1. Clona el repositorio y ábrelo en PyCharm (`Open` → selecciona la carpeta
   del proyecto).
2. Instala las dependencias:
   ```
   pip install selenium pytest
   ```
3. En `data.py`, reemplaza `URBAN_ROUTES_URL` por la URL de tu servidor
   (incluye `?lng=es`).
4. Asegúrate de tener instalado **ChromeDriver** compatible con tu versión
   de Chrome.
5. Ejecuta las pruebas desde la terminal:
   ```
   pytest main.py -v
   ```
6. Para excluir la prueba opcional (espera de asignación de conductor, que
   puede tardar hasta 60s):
   ```
   pytest main.py -v -m "not optional"
   ```

## Casos de prueba cubiertos

1. Configuración de la dirección de origen y destino
2. Selección de la tarifa Comfort
3. Llenado y verificación del número de teléfono
4. Registro de tarjeta de crédito (incluye manejo del enfoque del campo CVV)
5. Mensaje de texto para el conductor
6. Solicitud de manta y pañuelos
7. Solicitud de 2 helados
8. Aparición del modal de búsqueda de taxi
9. (Opcional) Espera hasta que se asigna un conductor y se muestra su información

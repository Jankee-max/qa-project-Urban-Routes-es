import json
import time

import data
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def retrieve_phone_code(driver) -> str:
    """
    Obtiene el código SMS desde el cuerpo de la respuesta de red
    (no desde la URL de la petición).
    """
    code = None

    for _ in range(10):
        try:
            logs = [
                log["message"] for log in driver.get_log("performance")
                if log.get("message") and "api/v1/number?number" in log.get("message")
            ]

            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody",
                    {"requestId": message_data["params"]["requestId"]}
                )
                code = "".join([x for x in body["body"] if x.isdigit()])
                if code:
                    break

            if code:
                break

        except WebDriverException:
            time.sleep(1)
            continue

        time.sleep(1)

    if not code:
        raise Exception(
            "No se pudo obtener el código de confirmación "
            "del teléfono."
        )

    return code


class UrbanRoutesPage:
    # Direcciones
    from_field = (By.ID, "from")
    to_field = (By.ID, "to")

    # Tarifas
    call_taxi_button = (
        By.XPATH,
        '//button[contains(text(), "Pedir un taxi")]'
    )

    comfort_rate_card = (
        By.XPATH,
        '//div[contains(@class, "tcard-title") and text()="Comfort"]'
    )

    # NUEVO: localizador para saber qué tarifa quedó realmente
    # seleccionada (no solo cuál es visible/clicable).
    # OJO: el nombre de la clase "active" es una suposición razonable
    # sobre cómo Urban Routes marca la tarjeta elegida. Verifícalo
    # abriendo las DevTools, haciendo clic en "Comfort" y mirando qué
    # clase le agrega el sitio al contenedor de la tarjeta (el padre
    # de "tcard-title"). Ajusta el nombre de la clase si es distinto.
    selected_rate_name = (
        By.XPATH,
        '//div[contains(@class, "tcard") and contains(@class, "active")]'
        '//div[contains(@class, "tcard-title")]'
    )

    # Teléfono
    phone_field_button = (By.CLASS_NAME, "np-text")
    phone_input = (By.ID, "phone")

    next_phone_button = (
        By.XPATH,
        '//button[contains(text(), "Siguiente")]'
    )

    confirmation_code_input = (By.ID, "code")

    confirm_phone_button = (
        By.XPATH,
        '//button[contains(text(), "Confirmar")]'
    )

    # Tarjeta de crédito
    payment_method_button = (By.CLASS_NAME, "pp-text")

    # NUEVO: localizador con By.CSS_SELECTOR que apunta al VALOR real
    # del método de pago. Confirmado por inspección del DOM: ".pp-text"
    # siempre dice la etiqueta fija "Método de pago" y NUNCA cambia;
    # el valor real ("Efectivo" / "Tarjeta") vive en un elemento
    # hermano con clase "pp-value-text", dentro de "pp-value":
    #   <div class="pp-button filled">
    #     <div class="pp-text">Método de pago</div>
    #     <div class="pp-value">
    #       <div class="pp-value-text">Efectivo</div>   <-- esto
    #       ...
    payment_method_value = (By.CSS_SELECTOR, ".pp-button .pp-value-text")

    # Fila "Agregar tarjeta" dentro del modal "Método de pago"
    add_card_button = (
        By.XPATH,
        '//div[contains(text(), "Agregar tarjeta")]'
    )

    card_number_input = (By.ID, "number")

    card_code_input = (
        By.XPATH,
        '//input[@id="code" and @class="card-input"]'
    )

    # Botón real: <button type="submit" class="button full">Agregar</button>
    # Se activa cuando el CVV pierde el foco (es el botón "link"/confirmar)
    card_link_button = (
        By.XPATH,
        '//button[contains(@class, "button") and normalize-space(text())="Agregar"]'
    )

    close_payment_modal_button = (
        By.XPATH,
        '//div[contains(@class, "payment-picker") '
        'and contains(@class, "open")]'
        '//button[contains(@class, "close-button")]'
    )

    # Mensaje al conductor
    comment_field = (By.ID, "comment")

    # Manta y pañuelos
    blanket_tissue_switch = (
        By.XPATH,
        '//div[contains(text(), "Manta y pañuelos")]'
        '/following-sibling::div'
        '//span[contains(@class, "slider")]'
    )

    blanket_tissue_checkbox = (
        By.XPATH,
        '//div[contains(text(), "Manta y pañuelos")]'
        '/following-sibling::div'
        '//input[@type="checkbox"]'
    )

    # Helados
    ice_cream_plus_button = (
        By.XPATH,
        '//div[contains(text(), "Helado")]'
        '/following-sibling::div'
        '//div[contains(@class, "counter-plus")]'
    )

    ice_cream_value = (
        By.XPATH,
        '//div[contains(text(), "Helado")]'
        '/following-sibling::div'
        '//div[contains(@class, "counter-value")]'
    )

    # Pedido y modal
    order_taxi_button = (
        By.XPATH,
        '//button[contains(@class, "smart-button")]'
    )

    order_modal = (By.CLASS_NAME, "order-body")

    driver_info_modal = (By.CLASS_NAME, "order-number")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def _click(self, locator):
        """Clic robusto: espera a que el elemento sea clicable y, si
        Selenium reporta que el clic fue interceptado por otro
        elemento (un overlay o un panel que todavía está animando su
        cierre), reintenta primero centrando el elemento en pantalla
        y, como último recurso, hace clic vía JavaScript (que no se
        ve bloqueado por overlays). Evita depender de adivinar el
        nombre exacto de la clase CSS que controla esa animación."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )
            try:
                element.click()
            except ElementClickInterceptedException:
                self.driver.execute_script(
                    "arguments[0].click();", element
                )

    # Direcciones
    def set_from(self, from_address):
        self.wait.until(
            EC.visibility_of_element_located(self.from_field)
        ).send_keys(from_address)

    def set_to(self, to_address):
        self.wait.until(
            EC.visibility_of_element_located(self.to_field)
        ).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(
            *self.from_field
        ).get_property("value")

    def get_to(self):
        return self.driver.find_element(
            *self.to_field
        ).get_property("value")

    # Tarifa
    def click_call_taxi_button(self):
        self.wait.until(
            EC.element_to_be_clickable(self.call_taxi_button)
        ).click()

    def select_comfort_rate(self):
        self._click(self.comfort_rate_card)

    def get_selected_rate_name(self):
        """Devuelve el nombre de la tarifa que quedó realmente
        seleccionada (no solo la que está visible)."""
        return self.wait.until(
            EC.visibility_of_element_located(self.selected_rate_name)
        ).text

    # Teléfono
    def fill_phone_number(self, phone):
        self.wait.until(
            EC.element_to_be_clickable(self.phone_field_button)
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(self.phone_input)
        ).send_keys(phone)

        self.wait.until(
            EC.element_to_be_clickable(self.next_phone_button)
        ).click()

        code = retrieve_phone_code(self.driver)

        self.wait.until(
            EC.visibility_of_element_located(
                self.confirmation_code_input
            )
        ).send_keys(code)

        self.wait.until(
            EC.element_to_be_clickable(self.confirm_phone_button)
        ).click()

        # Espera a que el modal del teléfono se cierre por completo
        # (incluido el overlay) antes de continuar con otras acciones.
        self.wait.until(
            EC.invisibility_of_element_located(self.confirm_phone_button)
        )

    def get_phone_number_text(self):
        return self.driver.find_element(
            *self.phone_field_button
        ).text

    # Tarjeta
    def add_credit_card(self, card_number, card_code):
        self.wait.until(
            EC.element_to_be_clickable(
                self.payment_method_button
            )
        ).click()

        # Clic en la fila "Agregar tarjeta" del modal "Método de pago"
        self.wait.until(
            EC.element_to_be_clickable(
                self.add_card_button
            )
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(
                self.card_number_input
            )
        ).send_keys(card_number)

        cvv_element = self.wait.until(
            EC.visibility_of_element_located(
                self.card_code_input
            )
        )

        cvv_element.send_keys(card_code)

        # El campo CVV debe perder el foco para activar
        # el botón "Agregar" (submit).
        cvv_element.send_keys(Keys.TAB)

        self.wait.until(
            EC.element_to_be_clickable(
                self.card_link_button
            )
        ).click()

        self.wait.until(
            EC.element_to_be_clickable(
                self.close_payment_modal_button
            )
        ).click()

        # Espera a que el modal de pago (y su overlay) desaparezca
        self.wait.until(
            EC.invisibility_of_element_located(self.close_payment_modal_button)
        )

    def get_payment_method_value(self):
        """Devuelve el VALOR del método de pago seleccionado
        (por ejemplo "Efectivo" o "Tarjeta"), no la etiqueta fija
        "Método de pago"."""
        return self.driver.find_element(
            *self.payment_method_value
        ).text

    def wait_for_payment_method_value(self, expected_text):
        """Espera explícitamente a que el texto del método de pago
        se actualice al valor esperado tras agregar la tarjeta."""
        self.wait.until(
            EC.text_to_be_present_in_element(
                self.payment_method_value, expected_text
            )
        )

    # Mensaje al conductor
    def set_message_for_driver(self, message):
        self.wait.until(
            EC.visibility_of_element_located(
                self.comment_field
            )
        ).send_keys(message)

    def get_message_for_driver(self):
        return self.driver.find_element(
            *self.comment_field
        ).get_property("value")

    # Manta y pañuelos
    def order_blanket_and_tissues(self):
        self._click(self.blanket_tissue_switch)

    def is_blanket_selected(self):
        return self.driver.find_element(
            *self.blanket_tissue_checkbox
        ).is_selected()

    # Helados
    def order_ice_cream(self, quantity=2):
        # Usamos self._click() (no un solo find + click repetido) en
        # cada vuelta, por si el primer clic dispara algún overlay o
        # reflow que intercepte el siguiente.
        for _ in range(quantity):
            self._click(self.ice_cream_plus_button)

    def get_ice_cream_count(self):
        return self.driver.find_element(
            *self.ice_cream_value
        ).text

    # Pedido
    def click_order_taxi(self):
        self._click(self.order_taxi_button)

    def is_search_modal_displayed(self):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.order_modal
            )
        ).is_displayed()

    # Paso opcional
    def wait_for_driver_info(self):
        return WebDriverWait(
            self.driver,
            40
        ).until(
            EC.visibility_of_element_located(
                self.driver_info_modal
            )
        ).is_displayed()


class TestUrbanRoutes:
    """
    Cada prueba abre su propio navegador (setup_method/teardown_method)
    y arma sus propias precondiciones a través de los helpers privados
    _open_app_and_set_route() y _open_order_form_with_comfort_rate().
    Así ninguna prueba depende del estado que haya dejado otra y todas
    pueden ejecutarse juntas o por separado.
    """

    def setup_method(self):
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.set_capability(
            "goog:loggingPrefs",
            {"performance": "ALL"}
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.routes_page = UrbanRoutesPage(self.driver)

    def teardown_method(self):
        if getattr(self, "driver", None) is not None:
            self.driver.quit()

    # --- Helpers de precondiciones (no son pruebas) ---

    def _open_app_and_set_route(self):
        self.driver.get(data.urban_routes_url)
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)

    def _open_order_form_with_comfort_rate(self):
        """Precondición común para las pruebas que actúan dentro del
        formulario de pedido: abre la app, ingresa las direcciones,
        abre el formulario de tarifas y selecciona Comfort."""
        self._open_app_and_set_route()
        self.routes_page.click_call_taxi_button()
        self.routes_page.select_comfort_rate()

    # --- Pruebas ---

    def test_set_route(self):
        self._open_app_and_set_route()

        assert self.routes_page.get_from() == data.address_from
        assert self.routes_page.get_to() == data.address_to

    def test_select_comfort_rate(self):
        self._open_app_and_set_route()
        self.routes_page.click_call_taxi_button()
        self.routes_page.select_comfort_rate()

        assert self.routes_page.get_selected_rate_name() == "Comfort"

    def test_fill_phone_number(self):
        self._open_order_form_with_comfort_rate()

        self.routes_page.fill_phone_number(data.phone_number)

        assert (
            data.phone_number
            in self.routes_page.get_phone_number_text()
        )

    def test_add_credit_card(self):
        self._open_order_form_with_comfort_rate()

        self.routes_page.add_credit_card(
            data.card_number,
            data.card_code
        )
        self.routes_page.wait_for_payment_method_value("Tarjeta")

        assert "Tarjeta" in self.routes_page.get_payment_method_value()

    def test_write_message_for_driver(self):
        self._open_order_form_with_comfort_rate()

        self.routes_page.set_message_for_driver(
            data.message_for_driver
        )

        assert (
            self.routes_page.get_message_for_driver()
            == data.message_for_driver
        )

    def test_order_blanket_and_tissues(self):
        self._open_order_form_with_comfort_rate()

        self.routes_page.order_blanket_and_tissues()

        assert self.routes_page.is_blanket_selected() is True

    def test_order_ice_cream(self):
        self._open_order_form_with_comfort_rate()

        self.routes_page.order_ice_cream(2)

        assert self.routes_page.get_ice_cream_count() == "2"

    def test_order_taxi_modal_appears(self):
        self._open_order_form_with_comfort_rate()

        self.routes_page.click_order_taxi()

        assert self.routes_page.is_search_modal_displayed() is True
import json
import time

import data
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
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
        self.wait.until(
            EC.element_to_be_clickable(self.comfort_rate_card)
        ).click()

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

    def get_payment_method_text(self):
        return self.driver.find_element(
            *self.payment_method_button
        ).text

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
        self.wait.until(
            EC.element_to_be_clickable(
                self.blanket_tissue_switch
            )
        ).click()

    def is_blanket_selected(self):
        return self.driver.find_element(
            *self.blanket_tissue_checkbox
        ).is_selected()

    # Helados
    def order_ice_cream(self, quantity=2):
        plus_button = self.wait.until(
            EC.element_to_be_clickable(
                self.ice_cream_plus_button
            )
        )

        for _ in range(quantity):
            plus_button.click()

    def get_ice_cream_count(self):
        return self.driver.find_element(
            *self.ice_cream_value
        ).text

    # Pedido
    def click_order_taxi(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.order_taxi_button
            )
        ).click()

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
    driver = None

    @classmethod
    def setup_class(cls):
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.set_capability(
            "goog:loggingPrefs",
            {"performance": "ALL"}
        )

        cls.driver = webdriver.Chrome(
            options=chrome_options
        )
        cls.driver.maximize_window()

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)

        routes_page = UrbanRoutesPage(self.driver)

        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)

        assert routes_page.get_from() == data.address_from
        assert routes_page.get_to() == data.address_to

    def test_select_comfort_rate(self):
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.click_call_taxi_button()
        routes_page.select_comfort_rate()

    def test_fill_phone_number(self):
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.fill_phone_number(
            data.phone_number
        )

        assert (
            data.phone_number
            in routes_page.get_phone_number_text()
        )

    def test_add_credit_card(self):
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.add_credit_card(
            data.card_number,
            data.card_code
        )

        # Verificamos que el método de pago ya no sea "Efectivo"
        # (cambió tras agregar y seleccionar la tarjeta)
        assert (
            "Efectivo"
            not in routes_page.get_payment_method_text()
        )

    def test_write_message_for_driver(self):
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.set_message_for_driver(
            data.message_for_driver
        )

        assert (
            routes_page.get_message_for_driver()
            == data.message_for_driver
        )

    def test_order_blanket_and_tissues(self):
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.order_blanket_and_tissues()

        assert (
            routes_page.is_blanket_selected()
            is True
        )

    def test_order_ice_cream(self):
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.order_ice_cream(2)

        assert (
            routes_page.get_ice_cream_count()
            == "2"
        )

    def test_order_taxi_modal_appears(self):
        routes_page = UrbanRoutesPage(self.driver)

        routes_page.click_order_taxi()

        assert (
            routes_page.is_search_modal_displayed()
            is True
        )

    @classmethod
    def teardown_class(cls):
        if cls.driver is not None:
            cls.driver.quit()
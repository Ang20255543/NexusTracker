#tokens.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


def get_token(user, password):

    options = webdriver.ChromeOptions()

    options.set_capability(
        "goog:loggingPrefs",
        {
            "performance": "ALL"
        }
    )

    driver = webdriver.Chrome(options=options)

    try:
        print("Abriendo Servicios en Línea de UANL...")

        driver.get("https://www.uanl.mx/enlinea/")

        wait = WebDriverWait(driver, 20)

        print("Buscando formulario de SIASE...")

        loginbox = wait.until(
            EC.presence_of_element_located((By.NAME, "loginbox"))
        )

        driver.switch_to.frame(loginbox)

        usuario = wait.until(
            EC.presence_of_element_located((By.ID, "cuenta"))
        )

        password_box = wait.until(
            EC.presence_of_element_located((By.ID, "pass"))
        )

        usuario.send_keys(user)
        password_box.send_keys(password)

        print("Enviando inicio de sesión...")

        boton = driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Entrar')]"
        )

        boton.click()

        driver.switch_to.default_content()

        time.sleep(5)

        print("Buscando acceso a Nexus...")

        nexus = wait.until(
            EC.presence_of_element_located((By.ID, "linkNexus"))
        )

        print("Elemento Nexus encontrado.")

        print("Abriendo Nexus...")

        driver.execute_script(
            "arguments[0].click();",
            nexus
        )

        time.sleep(10)

        print("Buscando ventana de Nexus...")

        ventanas = driver.window_handles

        for ventana in ventanas:

            driver.switch_to.window(ventana)

            if "plataformanexus.uanl.mx" in driver.current_url:

                print("Nexus encontrado.")

                break

        print("URL de Nexus:")
        print(driver.current_url)

        print("Esperando que Nexus cargue...")

        time.sleep(8)

        print("Leyendo localStorage...")

        sesion = driver.execute_script(
            "return localStorage.getItem('UanlNexus7Sesion');"
        )

        sesion_storage = driver.execute_script(
            "return localStorage.getItem('UanlNexus7SesionStorage');"
        )

        print()
        print("UanlNexus7Sesion encontrado:", sesion is not None)
        print("UanlNexus7SesionStorage encontrado:", sesion_storage is not None)

        if not sesion and not sesion_storage:

            print()
            print("No se encontró información de sesión en Nexus.")

            return None

        print()
        print("Analizando información de sesión...")

        # Intentamos obtener el token sin mostrarlo en pantalla
        for nombre, valor in [
            ("UanlNexus7Sesion", sesion),
            ("UanlNexus7SesionStorage", sesion_storage)
        ]:

            if not valor:
                continue

            print()
            print("Revisando:", nombre)

            try:

                datos = json.loads(valor)

                print("Formato JSON detectado.")

                if isinstance(datos, dict):

                    posibles = [
                        "token",
                        "Token",
                        "access_token",
                        "accessToken",
                        "jwt",
                        "Sesion",
                        "session",
                        "sessionToken"
                    ]

                    for clave in posibles:

                        if clave in datos:

                            encontrado = datos[clave]

                            if isinstance(encontrado, str):

                                print("Token encontrado.")

                                return encontrado

                            if isinstance(encontrado, dict):

                                for subclave in [
                                    "token",
                                    "Token",
                                    "access_token",
                                    "accessToken"
                                ]:

                                    if subclave in encontrado:

                                        print("Token encontrado.")

                                        return encontrado[subclave]

                print("No se encontró token en este objeto.")

            except json.JSONDecodeError:

                print("El valor no está en formato JSON.")

                # Si fuera directamente un token
                if len(valor) > 20:

                    print("Posible token encontrado.")

                    return valor

        print()
        print("No se encontró un token directamente.")

        print()
        print("Claves disponibles en localStorage:")

        claves = driver.execute_script(
            "return Object.keys(localStorage);"
        )

        for clave in claves:

            print("-", clave)

        return None

    except Exception as e:

        print()
        print("Error obteniendo token mediante navegador:")
        print(e)

        return None

    finally:

        driver.quit()


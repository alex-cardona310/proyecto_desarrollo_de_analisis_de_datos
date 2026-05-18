from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time

from tkinter import Tk, filedialog


class WebScraper:

    def save_file_dialog(self):

        root = Tk()
        root.withdraw()

        path = filedialog.asksaveasfilename(
            title="Guardar archivo TXT",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )

        root.destroy()

        return path

    def scrape_data(self):

        url = input("Ingresa la URL: ")

        options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(url)

        time.sleep(5)

        contenedor = input(
            "Ingresa la clase del contenedor principal de cada producto: "
        )

        productos = driver.find_elements(
            By.CLASS_NAME,
            contenedor
        )

        print(f"Productos encontrados: {len(productos)}")

        num_columnas = int(
            input("¿Cuántos datos quieres extraer?: ")
        )

        columnas = []

        for i in range(num_columnas):

            nombre = input(
                f"Nombre del dato {i+1}: "
            )

            etiqueta = input(
                f"Etiqueta HTML de {nombre}: "
            )

            clase = input(
                f"Clase HTML de {nombre}: "
            )

            columnas.append({
                "nombre": nombre,
                "etiqueta": etiqueta,
                "clase": clase
            })

        contenido_txt = ""

        for producto in productos:

            contenido_txt += "PRODUCTO\n"
            contenido_txt += "-" * 40 + "\n"

            for columna in columnas:

                try:

                    elemento = producto.find_element(
                        By.CSS_SELECTOR,
                        f"{columna['etiqueta']}.{columna['clase']}"
                    )

                    texto = elemento.text.strip()

                except:

                    texto = ""

                contenido_txt += (
                    f"{columna['nombre']}: {texto}\n"
                )

            contenido_txt += "\n"

        guardar = input(
            "\n¿Deseas guardar el resultado en TXT? (s/n): "
        ).lower()

        if guardar == "s":

            path = self.save_file_dialog()

            if path:

                with open(
                    path,
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(contenido_txt)

                print(
                    f"\nTXT guardado correctamente en:\n{path}"
                )

            else:

                print("Guardado cancelado.")

        driver.quit()
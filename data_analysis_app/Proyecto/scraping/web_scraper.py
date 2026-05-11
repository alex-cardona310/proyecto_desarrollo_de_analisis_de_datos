from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time

from tkinter import Tk, filedialog


class WebScraper:

    def __init__(self):
        self.df = None

    def save_file_dialog(self):

        root = Tk()
        root.withdraw()

        path = filedialog.asksaveasfilename(
            title="Guardar archivo CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
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
            input("¿Cuántas columnas quieres extraer?: ")
        )

        columnas = []

        for i in range(num_columnas):

            nombre_columna = input(
                f"Nombre de la columna {i+1}: "
            )

            etiqueta = input(
                f"Etiqueta HTML de {nombre_columna}: "
            )

            clase = input(
                f"Clase HTML de {nombre_columna}: "
            )

            columnas.append({
                "nombre": nombre_columna,
                "etiqueta": etiqueta,
                "clase": clase
            })

        datos = []

        for producto in productos:

            fila = []

            for columna in columnas:

                try:

                    elemento = producto.find_element(
                        By.CSS_SELECTOR,
                        f"{columna['etiqueta']}.{columna['clase']}"
                    )

                    texto = elemento.text.strip()

                except:

                    texto = ""

                fila.append(texto)

            datos.append(fila)

        encabezados = [
            columna["nombre"]
            for columna in columnas
        ]

        self.df = pd.DataFrame(
            datos,
            columns=encabezados
        )

        print("\nDataFrame generado correctamente:\n")

        print(self.df.head())

        guardar = input(
            "\n¿Deseas guardar el resultado en CSV? (s/n): "
        ).lower()

        if guardar == "s":

            path = self.save_file_dialog()

            if path:

                self.df.to_csv(
                    path,
                    index=False,
                    encoding="utf-8"
                )

                print(f"\nCSV guardado correctamente en:\n{path}")

            else:

                print("Guardado cancelado.")

        driver.quit()

        return self.df
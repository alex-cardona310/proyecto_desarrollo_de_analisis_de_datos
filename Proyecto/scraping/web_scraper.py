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

    def save_file_dialog(self, file_type):

        root = Tk()
        root.withdraw()

        if file_type == "csv":

            path = filedialog.asksaveasfilename(
                title="Save CSV file",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )

        elif file_type == "json":

            path = filedialog.asksaveasfilename(
                title="Save JSON file",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )

        elif file_type == "txt":

            path = filedialog.asksaveasfilename(
                title="Save TXT file",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )

        else:

            path = ""

        root.destroy()

        return path

    def scrape_data(self):

        url = input("Enter the URL: ")

        options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(url)

        time.sleep(5)

        contenedor = input(
            "Enter the main container class for each product: "
        )

        productos = driver.find_elements(
            By.CLASS_NAME,
            contenedor
        )

        print(f"\nProducts found: {len(productos)}")

        num_columnas = int(
            input("\nHow many columns do you want to extract?: ")
        )

        columnas = []

        for i in range(num_columnas):

            nombre_columna = input(
                f"\nName of column {i+1}: "
            )

            etiqueta = input(
                f"HTML tag for {nombre_columna}: "
            )

            clase = input(
                f"HTML class for {nombre_columna}: "
            )

            columnas.append({
                "nombre": nombre_columna,
                "etiqueta": etiqueta,
                "clase": clase
            })

        contenido_txt = ""

        datos = []

        for producto in productos:

            fila = []

            contenido_txt += "PRODUCT\n"
            contenido_txt += "-" * 40 + "\n"

            for columna in columnas:

                try:

                    elementos = producto.find_elements(
                        By.CSS_SELECTOR,
                        f"{columna['etiqueta']}.{columna['clase']}"
                    )

                    texto = " ".join([
                        elemento.text.strip()
                        for elemento in elementos
                        if elemento.text.strip() != ""
                    ])

                except:

                    texto = ""

                contenido_txt += (
                    f"{columna['nombre']}: {texto}\n"
                )

                fila.append(texto)

            contenido_txt += "\n"

            datos.append(fila)

        encabezados = [
            columna["nombre"]
            for columna in columnas
        ]

        self.df = pd.DataFrame(
            datos,
            columns=encabezados
        )

        self.df = self.df.dropna(how="all")

        self.df = self.df[
            ~(self.df.astype(str).apply(
                lambda row: row.str.strip().eq("").all(),
                axis=1
            ))
        ]

        self.df = self.df.reset_index(drop=True)

        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", None)

        print("\nDataFrame generated successfully.\n")

        print(self.df.head())

        while True:

            print("\nWhat would you like to do?")
            print("1. View first rows")
            print("2. View last rows")
            print("3. View DataFrame information")
            print("4. Save as CSV")
            print("5. Save as JSON")
            print("6. Save as TXT")
            print("7. Exit")

            opcion = input("\nChoose an option: ").strip()

            if opcion == "1":

                print("\nFirst rows of the DataFrame:\n")

                print(self.df.head(5))

            elif opcion == "2":

                print("\nLast rows of the DataFrame:\n")

                print(self.df.tail(5))

            elif opcion == "3":

                print("\nDataFrame information:\n")

                self.df.info()

            elif opcion == "4":

                path = self.save_file_dialog("csv")

                if path:

                    try:

                        self.df.to_csv(
                            path,
                            index=False,
                            encoding="utf-8-sig"
                        )

                        print(
                            f"\nCSV saved successfully at:\n{path}"
                        )

                    except PermissionError:

                        print(
                            "\nError: The CSV file is open."
                            "\nClose it and try again."
                        )

                    except Exception as e:

                        print(f"\nError saving CSV: {e}")

                else:

                    print("Save cancelled.")

            elif opcion == "5":

                path = self.save_file_dialog("json")

                if path:

                    try:

                        self.df.to_json(
                            path,
                            orient="records",
                            indent=4,
                            force_ascii=False
                        )

                        print(
                            f"\nJSON saved successfully at:\n{path}"
                        )

                    except PermissionError:

                        print(
                            "\nError: The JSON file is open."
                            "\nClose it and try again."
                        )

                    except Exception as e:

                        print(f"\nError saving JSON: {e}")

                else:

                    print("Save cancelled.")

            elif opcion == "6":

                path = self.save_file_dialog("txt")

                if path:

                    try:

                        with open(
                            path,
                            "w",
                            encoding="utf-8"
                        ) as file:

                            file.write(contenido_txt)

                        print(
                            f"\nTXT saved successfully at:\n{path}"
                        )

                    except PermissionError:

                        print(
                            "\nError: The TXT file is open."
                            "\nClose it and try again."
                        )

                    except Exception as e:

                        print(f"\nError saving TXT: {e}")

                else:

                    print("Save cancelled.")

            elif opcion == "7":

                break

            else:

                print("Invalid option.")

        driver.quit()

        return self.df
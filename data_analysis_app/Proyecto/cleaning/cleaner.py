class Cleaner:
    def __init__(self, df):
        self.df = df

    def eliminar_duplicados(self):
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        return self.df

    def eliminar_filas_nulas(self):
        self.df = self.df.dropna().reset_index(drop=True)
        return self.df

    def rellenar_espacios_vacios(self, columna):
        if columna not in self.df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")

        valor = input(f"Introduce el valor para rellenar espacios vacíos de '{columna}': ")

        self.df[columna] = self.df[columna].replace(r'^\s*$', None, regex=True)
        self.df[columna] = self.df[columna].fillna(valor)

        return self.df

    def convertir_tipo_columna(self, columna):
        if columna not in self.df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")

        print("Tipos disponibles: int, float, str, bool")
        tipo_usuario = input("Tipo de dato: ").strip().lower()

        tipos_validos = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool
        }

        if tipo_usuario not in tipos_validos:
            raise ValueError("Tipo no válido.")

        self.df[columna] = self.df[columna].astype(tipos_validos[tipo_usuario])
        return self.df

    def eliminar_outliers(self, columna):
        if columna not in self.df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")

        if not self.df[columna].dtype.kind in "biufc":
            raise ValueError(f"La columna '{columna}' debe ser numérica.")

        Q1 = self.df[columna].quantile(0.25)
        Q3 = self.df[columna].quantile(0.75)
        IQR = Q3 - Q1

        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR

        self.df = self.df[
            (self.df[columna] >= limite_inferior) &
            (self.df[columna] <= limite_superior)
        ].reset_index(drop=True)

        return self.df

    def validar_rango_columna(self, columna):
        if columna not in self.df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")

        minimo = float(input(f"Introduce el valor mínimo para '{columna}': "))
        maximo = float(input(f"Introduce el valor máximo para '{columna}': "))

        self.df = self.df[
            (self.df[columna] >= minimo) &
            (self.df[columna] <= maximo)
        ].reset_index(drop=True)

        return self.df

    def normalizar_dataframe(self):
        columnas_numericas = self.df.select_dtypes(include=["number"]).columns

        for columna in columnas_numericas:
            minimo = self.df[columna].min()
            maximo = self.df[columna].max()

            if maximo != minimo:
                self.df[columna] = (self.df[columna] - minimo) / (maximo - minimo)
            else:
                self.df[columna] = 0

        return self.df
    
    def guardar_limpio(self):
        import os
        import sqlite3

        print("Formatos disponibles:")
        print("1. CSV")
        print("2. TSV")
        print("3. SQL")

        opcion = input("Elige el formato para guardar el DataFrame limpio: ").strip()

        carpeta = input("Introduce la ruta de la carpeta donde quieres guardar el archivo: ").strip()

        if not os.path.exists(carpeta):
            raise ValueError("La carpeta indicada no existe.")

        nombre = input("Introduce el nombre del archivo o tabla sin extensión: ").strip()

        if opcion == "1":
            ruta = os.path.join(carpeta, f"{nombre}.csv")
            self.df.to_csv(ruta, index=False)
            print(f"DataFrame guardado correctamente en: {ruta}")

        elif opcion == "2":
            ruta = os.path.join(carpeta, f"{nombre}.tsv")
            self.df.to_csv(ruta, sep="\t", index=False)
            print(f"DataFrame guardado correctamente en: {ruta}")

        elif opcion == "3":
            ruta_db = os.path.join(carpeta, f"{nombre}.db")
            nombre_tabla = input("Introduce el nombre de la tabla SQL: ").strip()

            conexion = sqlite3.connect(ruta_db)
            self.df.to_sql(nombre_tabla, conexion, if_exists="replace", index=False)
            conexion.close()

            print(f"DataFrame guardado correctamente en la base de datos: {ruta_db}")
            print(f"Tabla creada/reemplazada: {nombre_tabla}")

        else:
            raise ValueError("Opción no válida. Elige 1, 2 o 3.")

        return self.df
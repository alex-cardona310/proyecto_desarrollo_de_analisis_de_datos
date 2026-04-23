class Cleaner:
    def __init__(self, rules=None):
        self.rules = rules if rules is not None else []

    def clean(self):
        pass

    def add_rule(self):
        pass

    def remove_rule(self):
        pass

    def apply(self):
        pass

    def _validateRules(self):
        pass

    def eliminar_duplicados(df):
        return df.drop_duplicates()
    
    def eliminar_filas_nulas(df):
        return df.dropna().reset_index(drop=True)
    
    
    
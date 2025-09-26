from src.db import WordsDatabase


def fill_db(database: WordsDatabase):
    if database.main_tables_exist():
        return
    database.create_tables()
    database.fill_table_main_words("Привет", "Hola")
    database.fill_table_main_words_variants(1, ["Hora", "Ola", "Hilo"])

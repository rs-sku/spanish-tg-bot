from src.db import WordsDatabase
from src.main_conf import MainConf


class Factory:
    def __init__(self):
        self._singleton = {}

    def create_database(self):
        if not self._singleton.get("WordsDatabase"):
            self._singleton["WordsDatabase"] = WordsDatabase(
                name=MainConf.POSTGRES_DATABASE,
                user=MainConf.POSTGRES_USER,
                password=MainConf.POSTGRES_PASSWORD,
                host=MainConf.POSTGRES_HOST,
            )
        return self._singleton["WordsDatabase"]


factory = Factory()

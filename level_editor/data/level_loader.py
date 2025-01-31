import json

class LevelLoader:

    @staticmethod
    def load_level(file_path):
        with open(file_path, "r") as file:
            return json.load(file)

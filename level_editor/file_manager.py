import json

class FileManager:

    @staticmethod
    def save_level(file_path, level_data):
        with open(file_path, "w") as file:
            json.dump(level_data, file, indent=4)

    @staticmethod
    def load_level(file_path):
        with open(file_path, "r") as file:
            return json.load(file)

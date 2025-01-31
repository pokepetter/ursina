import json

class LevelSaver:

    @staticmethod
    def save_level(file_path, level_data):
        with open(file_path, "w") as file:
            json.dump(level_data, file, indent=4)

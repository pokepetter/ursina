import json

class LevelEditor:

    def __init__(self):
        self.level_data = []
        self.current_level = None

    def new_level(self):
        self.level_data = []
        self.current_level = None
        print("New level created")

    def load_level(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.level_data = json.load(file)
                self.current_level = file_path
                print(f"Level loaded from {file_path}")
        except Exception as e:
            print(f"Failed to load level: {e}")

    def save_level(self, file_path):
        try:
            with open(file_path, 'w') as file:
                json.dump(self.level_data, file, indent=4)
                self.current_level = file_path
                print(f"Level saved to {file_path}")
        except Exception as e:
            print(f"Failed to save level: {e}")

    def add_object(self, obj):
        self.level_data.append(obj)
        print(f"Object {obj} added to the level")

    def remove_object(self, obj):
        if obj in self.level_data:
            self.level_data.remove(obj)
            print(f"Object {obj} removed from the level")
        else:
            print(f"Object {obj} not found in the level")

    def modify_object(self, obj, new_obj):
        if obj in self.level_data:
            index = self.level_data.index(obj)
            self.level_data[index] = new_obj
            print(f"Object {obj} modified to {new_obj}")
        else:
            print(f"Object {obj} not found in the level")

    def run(self):
        print("Running Level Editor...")

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()

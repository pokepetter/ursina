import os

def open_level_editor():
    os.system("python level_editor/editor.py")

def start_level_editor():
    print("Starting Level Editor...")
    open_level_editor()

if __name__ == "__main__":
    print("1. Start Game")
    print("2. Open Level Editor")
    choice = input("Choose an option: ")
    if choice == "2":
        start_level_editor()

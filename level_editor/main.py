import os

def open_level_editor():
    os.system("python level_editor/editor.py")

if __name__ == "__main__":
    print("1. Start Game")
    print("2. Open Level Editor")
    choice = input("Choose an option: ")
    if choice == "2":
        open_level_editor()

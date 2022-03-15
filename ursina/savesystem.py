import json
from ursina import application


save_data = dict()
save_file = application.asset_folder / f'{application.asset_folder.name}_savefile.json'

def load(name):
    if not save_data and save_file.exists():
        load_from_disk()

    if not name in save_data:
        return False

    return save_data[name]


def load_from_disk():
    global save_data
    save_data = json.load(file_name)

def save_to_disk():
    with open(file_name, 'w') as f:
        json.dump(save_data, f)


# def delete_from_disk():
#     pass

if __name__ == '__main__':
    load('a')

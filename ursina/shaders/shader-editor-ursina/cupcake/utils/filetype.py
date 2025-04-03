import filetype


class FileType:
    @staticmethod
    def get_file_type(file_path):
        return filetype.guess(file_path)
    
    @staticmethod
    def is_image(file_path):
        return filetype.is_image(file_path)

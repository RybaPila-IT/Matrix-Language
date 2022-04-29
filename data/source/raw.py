class RawFileSource:
    def __init__(self, filename: str):
        try:
            # Default open mode is reading.
            self.file = open(filename, encoding='utf-8')
        except IOError:
            raise

    def next_char(self):
        return self.file.read(1)

    def position(self):
        return self.file.tell()

    def set_position(self, position):
        self.file.seek(0)
        self.file.seek(position)

    def get_line(self):
        return self.file.readline()

    def __del__(self):
        try:
            self.file.close()
        except AttributeError:
            # This means that file attribute does not exist,
            # so the file opening operation failed.
            pass
        except IOError:
            raise


class RawStringSource:
    def __init__(self, content: str):
        self.content = content
        self.pos = -1

    def position(self):
        return self.pos + 1

    def next_char(self):
        self.pos = min(self.pos + 1, len(self.content))
        return (self.content[self.pos]
                if self.pos < len(self.content)
                else '')

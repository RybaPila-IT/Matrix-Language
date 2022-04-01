class RawFileSource:
    def __init__(self, filename: str):
        try:
            # Default open mode is reading.
            self.file = open(filename, encoding='utf-8')
        except IOError:
            raise

    def next_char(self):
        return self.file.read(1)

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
        self.position = 0

    def next_char(self):
        self.position = min(self.position + 1, len(self.content))
        return (self.content[self.position]
                if self.position < len(self.content)
                else '')

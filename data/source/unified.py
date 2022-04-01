class UnifiedSource:
    """
    Unified source unifies the characters fetched from RawSource.

    Unification is important in order to correctly distinguish
    new line characters among many operating systems.
    For example, on Linux machine new line is simply '\n'
    but on Microsoft Windows it is '\r\n'.

    Unified source casts every possible configuration into '\n'
    sign.
    """

    def __init__(self, raw_source):
        self.raw_source = raw_source
        self.finished = False
        self.is_buffered = False
        self.buffer = ''

    def next_char(self):
        if self.is_buffered:
            return self.__return_buffered_char()

        new_char = self.raw_source.next_char()

        if new_char == '\r':
            return self.__try_handle_windows_new_line()
        if new_char == '\025':
            return self.__try_handle_ibm_new_line()
        if new_char == '\n':
            return self.__try_handle_risc_and_linux_new_line()

        return new_char

    def __return_buffered_char(self):
        self.is_buffered = False
        return self.buffer

    def __try_handle_windows_new_line(self):
        new_char = self.raw_source.next_char()
        if new_char == '\n':
            # Here we know, that the sequence is '\r\n',
            # so we perform Windows unification
            return '\n'
        self.__buffer_char(new_char)
        return '\r'

    @staticmethod
    def __try_handle_ibm_new_line():
        return '\n'

    def __try_handle_risc_and_linux_new_line(self):
        new_char = self.raw_source.next_char()
        if new_char == '\r':
            # Here we know, that the sequence is '\n\r'
            # so we perform RISC OS unification
            return '\n'
        self.__buffer_char(new_char)
        return '\n'

    def __buffer_char(self, char):
        self.is_buffered = True
        self.buffer = char

class PositionalSource:
    """
    PositionalSource keeps track of the current position in the text.

    Is should use UnifiedSource in order to be accurate in counting
    current line number. UnifiedSource will provide single '\n' new line
    character, which is recognized by the PositionalSource.
    """
    def __init__(self, unified_source):
        self.unified_source = unified_source
        self.row_number = 1
        self.col_number = 1

    def next_char(self):
        next_char = self.unified_source.next_char()

        if next_char == '\n':
            self.row_number += 1
            self.col_number = 0
        elif next_char != '':
            self.col_number += 1

        return next_char

    def position(self):
        return (
            self.row_number,
            self.col_number
        )

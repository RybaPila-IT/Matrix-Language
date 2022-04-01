from data.source.raw import RawStringSource

if __name__ == '__main__':
    content = 'This is my text'
    raw_source = RawStringSource(content)
    for i in range(len(content)):
        print(raw_source.next_char())

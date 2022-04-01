from data.source.unified import UnifiedSource
from data.source.positional import PositionalSource
from data.source.raw import RawStringSource, RawFileSource


def unified_file_source_pipe(filename):
    return UnifiedSource(
        RawFileSource(filename)
    )


def unified_string_source_pipe(content):
    return UnifiedSource(
        RawStringSource(content)
    )


def positional_file_source_pipe(filename):
    return PositionalSource(
        unified_file_source_pipe(filename)
    )


def positional_string_source_pipe(content):
    return PositionalSource(
        unified_string_source_pipe(content)
    )

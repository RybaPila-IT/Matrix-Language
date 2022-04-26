import sys

from data.source.pipeline import positional_file_source_pipe
from lexical.analyzer import LexicalAnalyzer
from syntactic.analyzer import SyntacticAnalyzer
from execution.interpreter import Interpreter

arguments_err_mess = '''
Expected single argument with file name containing the source code of the program. 
Got {} arguments instead.
'''


def start_interpretation(file_name):
    # TODO (radek.r) Add real exception handler handling the lexical, syntactic and runtime errors as well.
    try:
        interpreter = interpreter_construction_pipeline(file_name)
        interpreter.execute()
    except IOError as e:
        print(e)
        return


def interpreter_construction_pipeline(file_name):
    return Interpreter(
        SyntacticAnalyzer(
            LexicalAnalyzer(
                positional_source=positional_file_source_pipe(file_name)
            )
        )
    )


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print(str.format(arguments_err_mess, len(arguments)))
    else:
        start_interpretation(arguments[0])


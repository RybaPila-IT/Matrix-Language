import sys

from data.source.pipeline import positional_file_source_pipe
from lexical.analyzer import LexicalAnalyzer
from lexical.exception import LexicalException
from syntactic.analyzer import SyntacticAnalyzer
from syntactic.exception import SyntacticException
from execution.interpreter import Interpreter
from execution.exception import ExecutionException
from exception.handler import ExceptionHandler


arguments_err_mess = '''
Expected single argument with file name containing the source code of the program. 
Got {} arguments instead.
'''


def start_interpretation(file_name):
    # Separate data source handling since it may be used for lexical
    # exceptions reporting.
    try:
        data_source = positional_file_source_pipe(file_name)
    except IOError as e:
        print(e)
        return

    try:
        interpreter = Interpreter(SyntacticAnalyzer(LexicalAnalyzer(data_source)))
        interpreter.execute()
    except LexicalException as e:
        ExceptionHandler.handle_lexical_exception(e, data_source.unified_source.raw_source)
    except SyntacticException as e:
        ExceptionHandler.handle_syntactic_exception(e, data_source.unified_source.raw_source)
    except ExecutionException as e:
        ExceptionHandler.handle_execution_exception(e)


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print(str.format(arguments_err_mess, len(arguments)))
    else:
        start_interpretation(arguments[0])


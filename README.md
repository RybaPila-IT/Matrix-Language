# Matrix Language Interpreter

### Author: Radosław Radziukiewicz


## Overview

Matrix language **(Mat-Lan)** is a custom programming language which supports matrix data type. 
It is heavily inspired by Python programming language and is implemented with the usage 
of Python itself.  


## Paradigms

Mat-Lan is an imperative language. It is dynamically typed. It supports lexical scope 
mechanism. <br>
Although variables are dynamically typed, the language does not allow to change the 
variable underlying type while program execution.
*If something is type A, it must stay a type A.*


## Data types

Mat-Lan supports three in-build data types:

- Matrices 
- Numbers 
- Strings

**Matrices** support multiplication, addition and subtraction by both number and matrix. 
Division is allowed by number only. Comparison is allowed only with other matrix.
<br>
**Numbers** support multiplication, division, addition, subtraction and comparison.
<br>
**Strings** do not support any operations.


## Boolean casting

Mat-Lan does not offer boolean type. It is present in the language only as the result of 
logic and comparison operations. <br>

Language performs below casts, when no comparison is performed:
- **Empty String is equal to False** <br>
- **Zero number is equal to False** <br>
- **All zero-entries matrix is equal to False** <br>


## Constructions


Mat-Lan supports following programming constructions:

- If ... else statement
- Until statement (equivalent to while loop in most of the languages)
- Return statements
- Function definition 
- Function calls
- Recursion

See examples section for better understanding.


## Grammar 


Below one can see the grammar, which describes implemented language:


```
program         = { funcDefinition }
funcDefinition  = identifier "(" parameters ")" statementBlock
parameters      = [ identifier { "," identifier } ] 
statementBlock  =  "{" {
                        ifStatement |
                        untilStatement |
                        returnStatement |
                        assignOrFuncCall |
                        statementBlock
                    } "}"

returnStatement     = "return" [ addExpression ]
ifStatement         = "if" "(" orCondition ")" statementBlock
                      [ "else" ( ifStatement | statementBlock ) ]
untilStatement      = "until" "(" orCondition ")" statementBlock
assignOrFuncCall    = identifier ( 
                                    ( "(" arguments ")" ) |
                                    ( [ indexOperator ] "=" addExpression )
                                  )
arguments           = [ addExpression { "," addExpression } ]

addExpression       = mulExpression { ("+" | "-") mulExpression }
mulExpression       = atomicExpression { ("*" | "/") atomicExpression }
atomicExpression    = ["-"] ( identOrFuncCall | literal | "(" orCondition ")" )
identOrFuncCall     = identifier [ "(" arguments ")" | indexOperator ]
indexOperator       = "[" selector "," selector "]"
selector            = ( ":" | addExpression )

orCondition         = andCondition { "or" andCondition }
andCondition        = relCondition { "and" relCondition }
relCondition        = ["!"] addExpression [ relOperator addExpression ]

literal             = matrixLiteral | numberLiteral | string
matrixLiteral       = "[" addExpression { ( "," | ";" ) addExpression } "]"

numberLiteral = (0|[1-9][0-9]*)(.[0-9]*)?
identifier    = [a-zA-z][a-zA-Z0-9_-]*
string        = "[Alfa-numeric characters]*"
```

Note: Grammar does not support semantic correctness of the program in all cases.


## Examples

Language usage examples can be found [here](https://github.com/RybaPila-IT/Matrix-Language/tree/main/programs).


## Tests

There are 103 test implemented for almost all modules of the program.

In order to run tests one should type the following command 
at the root directory of the following repository:

```shell
python -m unittest discover --verbose --start-directory test --top-level-directory .
```




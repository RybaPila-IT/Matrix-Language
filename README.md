# Matrix Language Interpreter

### Author: Radoslaw Radziukiewicz

---

This repository contains code implementing custom 
programming language, which supports matrices 
as data types.

## Tests

---

In order to run tests one should type the following command 
at the root directory of the following repository:

```shell
python -m unittest discover --verbose --start-directory test --top-level-directory .
```

## Grammar 

---

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



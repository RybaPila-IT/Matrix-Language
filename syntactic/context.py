from enum import Enum, auto


class SyntacticContext(Enum):
    FunctionDefinition = auto(),
    StatementBlock = auto(),
    Parameters = auto(),
    IfStatement = auto(),
    UntilStatement = auto(),
    FunctionCall = auto(),
    Assignment = auto(),
    IndexOperator = auto(),
    AdditiveExpression = auto(),
    MultiplicativeExpression = auto(),
    AtomicExpression = auto(),
    OrCondition = auto(),
    AndCondition = auto(),
    RelationCondition = auto(),
    Arguments = auto(),
    MatrixLiteral = auto()

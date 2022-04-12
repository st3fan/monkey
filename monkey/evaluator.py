# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import List, Optional, Union

from monkey.ast import BooleanLiteral, CallExpression, Expression, FunctionLiteral, IfExpression, InfixExpression, LetStatement, Node, IntegerLiteral, PrefixExpression, Program, ReturnStatement, Statement, ExpressionStatement, BlockStatement, Identifier, StringLiteral
from monkey.environment import Environment
from monkey.object import EvaluationError, Function, Object, Integer, Boolean, Null, ObjectType, ReturnValue, String


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)


def make_boolean(value: bool) -> Boolean:
    return TRUE if value else FALSE


def is_truthy(object: Object) -> bool:
    return object not in (NULL, FALSE)


def extend_function_env(function: Function, arguments: List[Object]) -> Environment:
    env = Environment(outer=function.environment)
    for i, parameter in enumerate(function.parameters):
        env.set(parameter.value, arguments[i])
    return env


def unwrap_return_value(object: Object) -> Object:
    if isinstance(object, ReturnValue):
        return object.value
    return object


class Evaluator:
    def eval_program(self, statements: List[Statement], environment: Environment) -> Object:
        result: Object = NULL
        for statement in statements:
            result = self.eval(statement, environment)
            if isinstance(result, ReturnValue):
                return result.value
            if isinstance(result, EvaluationError):
                return result
        return result

    def eval_block_statement(self, statements: List[Statement], environment: Environment) -> Object:
        result: Object = NULL
        for statement in statements:
            result = self.eval(statement, environment)
            if isinstance(result, ReturnValue) or isinstance(result, EvaluationError):
                return result
        return result

    def eval_let_statement(self, identifier: str, value: Object, environment: Environment) -> Object:
        environment.set(identifier, value)
        return NULL # Needed?

    def eval_if_expression(self, condition: Expression, consequence: BlockStatement, alternative: Optional[BlockStatement], environment: Environment) -> Object:
        if is_truthy(self.eval(condition, environment)):
            return self.eval(consequence, environment)
        elif alternative is not None:
            return self.eval(alternative, environment)
        return NULL

    def eval_prefix_expression(self, operator: str, right: Object) -> Object:
        match (operator, right):
            case ("-", Integer(value)):
                return Integer(-value)
            case ("!", Integer(value)):
                return make_boolean(value == 0)
            case ("!", Boolean(value)):
                return make_boolean(not value)
            case ("!", Null()):
                return TRUE
        return EvaluationError(f"unknown operator: {operator}{right.type()}")

    def eval_expressions(self, expressions: List[Expression], environment: Environment) -> List[Object]:
        results: List[Object] = []
        for expression in expressions:
            result = self.eval(expression, environment)
            if isinstance(result, EvaluationError):
                return [result]
            results.append(result)
        return results

    def eval_infix_expression(self, left: Object, operator: str, right: Object) -> Object:
        match (left, operator, right):
            case (left, "==", right):
                return make_boolean(left == right)
            case (left, "!=", right):
                return make_boolean(left != right)
            case (Integer(left_value), _, Integer(right_value)):
                match operator:
                    case "+":
                        return Integer(left_value + right_value)
                    case "-":
                        return Integer(left_value - right_value)
                    case "*":
                        return Integer(left_value * right_value)
                    case "/":
                        return Integer(left_value // right_value)
                    case "<":
                        return make_boolean(left_value < right_value)
                    case ">":
                        return make_boolean(left_value > right_value)
                    case _:
                        return EvaluationError(f"unknown operator: {left.type()} {operator} {right.type()}")
            case (String(left_value), _, String(right_value)):
                match operator:
                    case "+":
                        return String(left_value + right_value)
                    case "<":
                        return make_boolean(left_value < right_value)
                    case ">":
                        return make_boolean(left_value > right_value)
                    case _:
                        return EvaluationError(f"unknown operator: {left.type()} {operator} {right.type()}")
            case (Boolean(left_value), _, Boolean(right_value)):
                return EvaluationError(f"unknown operator: {left.type()} {operator} {right.type()}")
        return EvaluationError(f"type mismatch: {left.type()} {operator} {right.type()}")

    def apply_function(self, function: Object, arguments: List[Object]) -> Object:
        if not isinstance(function, Function):
            return EvaluationError(f"not a function: {function.type()}")
        extended_env = extend_function_env(function, arguments)
        evaluated = self.eval(function.body, extended_env)
        return unwrap_return_value(evaluated)

    # TODO This is now a mix of code and eval_* methods. Straighten that out.
    def eval(self, node: Node, environment: Environment) -> Object:
        match node:
            # Statements
            case Program(statements):
                return self.eval_program(statements, environment)
            case ExpressionStatement(expression):
                return self.eval(expression, environment)
            case BlockStatement(statements):
                return self.eval_block_statement(statements, environment)
            case ReturnStatement(expression):
                return ReturnValue(self.eval(expression, environment))
            case LetStatement(identifier, expression):
                value = self.eval(expression, environment)
                if isinstance(value, EvaluationError):
                    return value
                return self.eval_let_statement(identifier.value, value, environment)
            # Expressions
            case IfExpression(condition, consequence, alternative):
                return self.eval_if_expression(condition, consequence, alternative, environment)
            case IntegerLiteral(value):
                return Integer(value)
            case StringLiteral(value):
                return String(value)
            case BooleanLiteral(value):
                return make_boolean(value)
            case FunctionLiteral(parameters, body):
                return Function(parameters, body, environment)
            
            case CallExpression(function, arguments):
                fn = self.eval(function, environment)
                if isinstance(fn, EvaluationError):
                    return fn
                args = self.eval_expressions(arguments, environment)
                if len(args) == 1 and isinstance(args[0], EvaluationError):
                    return args[0]
                return self.apply_function(fn, args)

            case Identifier(name):
                if val := environment.get(name):
                    return val
                return EvaluationError(f"identifier not found: {name}")
            case PrefixExpression(operator, right_expression):
                right = self.eval(right_expression, environment)
                if isinstance(right, EvaluationError):
                    return right
                return self.eval_prefix_expression(operator, right)            
            case InfixExpression(left_expression, operator, right_expression):
                left = self.eval(left_expression, environment)
                if isinstance(left, EvaluationError):
                    return left
                right = self.eval(right_expression, environment)
                if isinstance(right, EvaluationError):
                    return right
                return self.eval_infix_expression(left, operator, right)
        return NULL

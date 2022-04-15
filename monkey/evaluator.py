# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from typing import List, Optional, Union

from monkey.ast import *
from monkey.builtins import BUILTINS
from monkey.environment import Environment
from monkey.object import *


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

    def apply_function(self, function: Union[Builtin, Function], arguments: List[Object]) -> Object:
        # TODO Should be a match
        if isinstance(function, Builtin):
            return function.value(arguments)
        if isinstance(function, Function):
            extended_env = extend_function_env(function, arguments)
            evaluated = self.eval(function.body, extended_env)
            return unwrap_return_value(evaluated)
        return EvaluationError(f"not a function: {function}") # TODO Fix

    def eval_array_literal(self, expressions: List[Expression], environment: Environment) -> Object:
        elements = self.eval_expressions(expressions, environment)
        if len(elements) == 1 and isinstance(elements[0], EvaluationError):
            return elements[0]
        return Array(elements)

    def eval_array_index_expression(self, array: Array, index: Integer) -> Object:
        if index.value < 0 or index.value > len(array.elements) - 1:
            return NULL
        return array.elements[index.value]

    def eval_hash_literal(self, pairs: Dict[Expression, Expression], environment: Environment) -> Union[EvaluationError, Hash]:
        evaluated_pairs: Dict[Object, Object] = {}
        for key_expression, value_expression in pairs.items():
            key = self.eval(key_expression,environment)
            if isinstance(key, EvaluationError):
                return key
            value = self.eval(value_expression,environment)
            if isinstance(value, EvaluationError):
                return value
            evaluated_pairs[key] = value
        return Hash(evaluated_pairs)

    def eval_index_expression(self, left: Object, index: Object) -> Object:
        if isinstance(left, Array) and isinstance(index, Integer):
            return self.eval_array_index_expression(left, index)
        return EvaluationError(f"index operator not supported: {left.type()}")

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
            case ArrayLiteral(expressions):
                return self.eval_array_literal(expressions, environment)
            case HashLiteral(pairs):
                return self.eval_hash_literal(pairs, environment)
            case IndexExpression(left_expression, index_expression):
                left = self.eval(left_expression, environment)
                index = self.eval(index_expression, environment)
                return self.eval_index_expression(left, index)
            
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
                if builtin := BUILTINS.get(name):
                    return builtin
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

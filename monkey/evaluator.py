# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from operator import truediv
from typing import List, Optional

from monkey.ast import BooleanLiteral, Expression, IfExpression, InfixExpression, Node, IntegerLiteral, PrefixExpression, Program, ReturnStatement, Statement, ExpressionStatement, BlockStatement
from monkey.object import EvaluationError, Object, Integer, Boolean, Null, ObjectType, ReturnValue


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)


def make_boolean(value: bool) -> Boolean:
    return TRUE if value else FALSE


def is_truthy(object: Object) -> bool:
    return object not in (NULL, FALSE)


class Evaluator:
    def eval_program(self, statements: List[Statement]) -> Object:
        result: Object = NULL
        for statement in statements:
            result = self.eval(statement)
            if isinstance(result, ReturnValue):
                return result.value
            if isinstance(result, EvaluationError):
                return result
        return result

    def eval_block_statement(self, statements: List[Statement]) -> Object:
        result: Object = NULL
        for statement in statements:
            result = self.eval(statement)
            if isinstance(result, ReturnValue) or isinstance(result, EvaluationError):
                return result
        return result

    def eval_if_expression(self, condition: Expression, consequence: BlockStatement, alternative: Optional[BlockStatement]) -> Object:
        if is_truthy(self.eval(condition)):
            return self.eval(consequence)
        elif alternative is not None:
            return self.eval(alternative)
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
            case (Boolean(left_value), _, Boolean(right_value)):
                return EvaluationError(f"unknown operator: {left.type()} {operator} {right.type()}")
        return EvaluationError(f"type mismatch: {left.type()} {operator} {right.type()}")

    def eval(self, node: Node) -> Object:
        match node:
            # Statements
            case Program(statements):
                return self.eval_program(statements)
            case ExpressionStatement(expression):
                return self.eval(expression)
            case BlockStatement(statements):
                return self.eval_block_statement(statements)
            case ReturnStatement(expression):
                return ReturnValue(self.eval(expression))
            # Expressions
            case IfExpression(condition, consequence, alternative):
                return self.eval_if_expression(condition, consequence, alternative)
            # Literal Expressions
            case IntegerLiteral(value):
                return Integer(value)
            case BooleanLiteral(value):
                return make_boolean(value)
            
            # Expressions
            case PrefixExpression(operator, right_expression):
                right = self.eval(right_expression)
                if isinstance(right, EvaluationError):
                    return right
                return self.eval_prefix_expression(operator, right)
            
            case InfixExpression(left_expression, operator, right_expression):
                left = self.eval(left_expression)
                if isinstance(left, EvaluationError):
                    return left
                right = self.eval(right_expression)
                if isinstance(right, EvaluationError):
                    return right
                return self.eval_infix_expression(left, operator, right)

            # Infix Expressions
            # case InfixExpression(left, "+", right):
            #     return self.eval_infix_plus_operator_expression(self.eval(left), self.eval(right))
            # case InfixExpression(left, "-", right):
            #     return self.eval_infix_minus_operator_expression(self.eval(left), self.eval(right))
            # case InfixExpression(left, "*", right):
            #     return self.eval_infix_star_operator_expression(self.eval(left), self.eval(right))
            # case InfixExpression(left, "/", right):
            #     return self.eval_infix_slash_operator_expression(self.eval(left), self.eval(right))
            # case InfixExpression(left, "<", right):
            #     return self.eval_infix_lt_operator_expression(self.eval(left), self.eval(right))
            # case InfixExpression(left, ">", right):
            #     return self.eval_infix_gt_operator_expression(self.eval(left), self.eval(right))
            # case InfixExpression(left, "==", right):
            #     return self.eval_infix_eq_operator_expression(self.eval(left), self.eval(right))
            # case InfixExpression(left, "!=", right):
            #     return self.eval_infix_ne_operator_expression(self.eval(left), self.eval(right))
        return NULL

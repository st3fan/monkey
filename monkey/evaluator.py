# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from operator import truediv
from typing import List, Optional

from monkey.ast import BooleanLiteral, Expression, IfExpression, InfixExpression, Node, IntegerLiteral, PrefixExpression, Program, Statement, ExpressionStatement, BlockStatement
from monkey.object import Object, Integer, Boolean, Null, ObjectType


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)


def make_boolean(value: bool) -> Boolean:
    return TRUE if value else FALSE


def is_truthy(object: Object) -> bool:
    return object not in (NULL, FALSE)


class Evaluator:
    def eval_statements(self, statements: List[Statement]) -> Object:
        result: Object = NULL
        for statement in statements:
            result = self.eval(statement)
        return result

    def eval_if_expression(self, condition: Expression, consequence: BlockStatement, alternative: Optional[BlockStatement]) -> Object:
        if is_truthy(self.eval(condition)):
            return self.eval(consequence)
        elif alternative is not None:
            return self.eval(alternative)
        return NULL

    def eval_prefix_bang_operator_expression(self, object: Object) -> Object:
        match object:
            case Integer(value):
                return TRUE if not value else FALSE
            case Boolean(True):
                return FALSE
            case Boolean(False):
                return TRUE
            case Null():
                return TRUE
        return NULL

    def eval_minus_prefix_operator_expression(self, object: Object) -> Object:
        if isinstance(object, Integer):
            return Integer(-object.value)
        return NULL

    def eval_infix_plus_operator_expression(self, left: Object, right: Object) -> Object:
        if isinstance(left, Integer) and isinstance(right, Integer):
            return Integer(left.value + right.value)
        return NULL

    def eval_infix_minus_operator_expression(self, left: Object, right: Object) -> Object:
        if isinstance(left, Integer) and isinstance(right, Integer):
            return Integer(left.value - right.value)
        return NULL

    def eval_infix_star_operator_expression(self, left: Object, right: Object) -> Object:
        if isinstance(left, Integer) and isinstance(right, Integer):
            return Integer(left.value * right.value)
        return NULL

    def eval_infix_slash_operator_expression(self, left: Object, right: Object) -> Object:
        if isinstance(left, Integer) and isinstance(right, Integer):
            return Integer(left.value // right.value)
        return NULL

    def eval_infix_lt_operator_expression(self, left: Object, right: Object) -> Object:
        if isinstance(left, Integer) and isinstance(right, Integer):
            return make_boolean(left.value < right.value)
        return NULL

    def eval_infix_gt_operator_expression(self, left: Object, right: Object) -> Object:
        if isinstance(left, Integer) and isinstance(right, Integer):
            return make_boolean(left.value > right.value)
        return NULL

    def eval_infix_eq_operator_expression(self, left: Object, right: Object) -> Object:
        return make_boolean(left == right)

    def eval_infix_ne_operator_expression(self, left: Object, right: Object) -> Object:
        return make_boolean(left != right)

    def eval(self, node: Node) -> Object:
        match node:
            # Statements
            case Program(statements):
                return self.eval_statements(statements)
            case ExpressionStatement(expression):
                return self.eval(expression)
            case BlockStatement(statements):
                return self.eval_statements(statements)
            case IfExpression(condition, consequence, alternative):
                return self.eval_if_expression(condition, consequence, alternative)
            # Literal Expressions
            case IntegerLiteral(value):
                return Integer(value)
            case BooleanLiteral(value):
                return make_boolean(value)
            # Prefix Expressions
            case PrefixExpression("!", right):
                return self.eval_prefix_bang_operator_expression(self.eval(right))
            case PrefixExpression("-", right):
                return self.eval_minus_prefix_operator_expression(self.eval(right))
            # Infix Expressions
            case InfixExpression(left, "+", right):
                return self.eval_infix_plus_operator_expression(self.eval(left), self.eval(right))
            case InfixExpression(left, "-", right):
                return self.eval_infix_minus_operator_expression(self.eval(left), self.eval(right))
            case InfixExpression(left, "*", right):
                return self.eval_infix_star_operator_expression(self.eval(left), self.eval(right))
            case InfixExpression(left, "/", right):
                return self.eval_infix_slash_operator_expression(self.eval(left), self.eval(right))
            case InfixExpression(left, "<", right):
                return self.eval_infix_lt_operator_expression(self.eval(left), self.eval(right))
            case InfixExpression(left, ">", right):
                return self.eval_infix_gt_operator_expression(self.eval(left), self.eval(right))
            case InfixExpression(left, "==", right):
                return self.eval_infix_eq_operator_expression(self.eval(left), self.eval(right))
            case InfixExpression(left, "!=", right):
                return self.eval_infix_ne_operator_expression(self.eval(left), self.eval(right))
        return NULL

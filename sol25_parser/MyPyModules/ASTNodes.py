"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           ASTNodes.py                                                *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file ASTNodes.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

from MyPyModules.CustomErrors import InternalError

class ASTNodes:
    class ASTAbstractNode:
        def visit_by(self, visitor):
            raise InternalError()

    class ProgramNode(ASTAbstractNode):
        def __init__(self, classes:list):
            self.classNodeList = classes

        def visit_by(self, visitor):
            return visitor.visit_program_node(self)

    class ClassNode(ASTAbstractNode):
        def __init__(self, identifier:str, fatherIdentifier:str, methods:list):
            self.id = identifier
            self.father = fatherIdentifier
            self.methodNodeList = methods

        def visit_by(self, visitor):
            return visitor.visit_class_node(self)

    class MethodNode(ASTAbstractNode):
        def __init__(self, selector:str, blocks:list):
            self.selector = selector
            self.blockNodeList = blocks

        def visit_by(self, visitor):
            return visitor.visit_method_node(self)

    class BlockNode(ASTAbstractNode):
        def __init__(self, parameters:list, statements:list):
            self.paramNodeList = parameters
            self.statementNodeList = statements

        def visit_by(self, visitor):
            return visitor.visit_block_node(self)

    class VarNode(ASTAbstractNode):
        def __init__(self, identifier):
            self.varId = identifier

        def visit_by(self, visitor):
            return visitor.visit_var_node(self)

    class LiteralNode(ASTAbstractNode):
        def __init__(self, type, value):
            self.literalType = type
            self.literalValue = value

        def visit_by(self, visitor):
            return visitor.visit_literal_node(self)

    class AssignNode(ASTAbstractNode):
        def __init__(self, variable, expression):
            self.varNode = variable
            self.exprNode = expression

        def visit_by(self, visitor):
            return visitor.visit_assign_node(self)

    class SendNode(ASTAbstractNode):
        def __init__(self, receiver, selector, args):
            self.receiver = receiver
            self.selector = selector
            self.argNodeList = args

        def visit_by(self, visitor):
            return visitor.visit_send_node(self)

class ASTNodeVisitor:
    def visit_program_node(self, ASTnode):
        raise InternalError()

    def visit_block_node(self, ASTnode):
        raise InternalError()

    def visit_class_node(self, ASTnode):
        raise InternalError()

    def visit_method_node(self, ASTnode):
        raise InternalError()

    def visit_send_node(self, ASTnode):
        raise InternalError()

    def visit_assign_node(self, ASTnode):
        raise InternalError()

    def visit_var_node(self, ASTnode):
        raise InternalError()

    def visit_literal_node(self, ASTnode):
        raise InternalError()

### konec souboru 'ASTNodes.py' ###

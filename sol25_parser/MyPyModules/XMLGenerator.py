"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           XMLGenerator.py                                            *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file XMLGenerator.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from MyPyModules.ASTNodes import ASTNodes as AST

class XMLGenerator:
    def __init__(self):
        pass

    def generate_XML(self, ASTRoot, firstComment):
        attrib = {"language": "SOL25"}
        if firstComment:
            # Nahrazení mezer a nových řádků entitou &nbsp;
            desc = firstComment[1:-1].replace("\n", "&nbsp;")
            attrib["description"] = desc
        program_el = ET.Element("program", attrib=attrib)

        # Pro každou uživatelsky definovanou třídu vytvoříme element <class>.
        order = 1
        for classNode in ASTRoot.classNodeList:
            class_el = self.generate_class(classNode, order)
            program_el.append(class_el)
            order += 1

        # Vrátíme hezky formátovaný XML řetězec s hlavičkou.
        rough_string = ET.tostring(program_el, encoding="utf-8")
        reparsed = minidom.parseString(rough_string)
        xml_bytes = reparsed.toprettyxml(indent="  ", encoding="UTF-8")
        xml_string = xml_bytes.decode("UTF-8")
        return xml_string

    def generate_class(self, classNode: AST.ClassNode, order: int) -> ET.Element:
        # Element <class> s atributy name a parent.
        attrib = {
            "name": classNode.id,
            "parent": classNode.father if classNode.father else ""
        }
        class_el = ET.Element("class", attrib=attrib)
        # Generujeme elementy pro každou definovanou metodu.
        for methodNode in classNode.methodNodeList:
            method_el = self.generate_method(methodNode)
            class_el.append(method_el)
        return class_el

    def generate_method(self, methodNode: AST.MethodNode) -> ET.Element:
        # Element <method> s atributem selector.
        attrib = {"selector": methodNode.selector}
        method_el = ET.Element("method", attrib=attrib)
        # Tělo metody je reprezentováno blokem.
        block_el = self.generate_block(methodNode.blockNode)
        method_el.append(block_el)
        return method_el

    def generate_block(self, blockNode: AST.BlockNode) -> ET.Element:
        # Element <block> s atributem arity udávajícím počet parametrů.
        arity = len(blockNode.paramNodeList) if blockNode.paramNodeList else 0
        block_el = ET.Element("block", attrib={"arity": str(arity)})
        # Generujeme podelementy pro každý parametr.
        param_order = 1
        for param in blockNode.paramNodeList:
            param_attrib = {"name": param, "order": str(param_order)}
            param_el = ET.Element("parameter", attrib=param_attrib)
            block_el.append(param_el)
            param_order += 1
        # Pro každý příkaz (přiřazení) v bloku vytvoříme element <assign>.
        for stmt in blockNode.statementNodeList:
            assign_el = self.generate_assign(stmt)
            block_el.append(assign_el)
        return block_el

    def generate_assign(self, assignNode: AST.AssignNode) -> ET.Element:
        # Element <assign> – podle specifikace nemá atribut order.
        assign_el = ET.Element("assign")
        # Podelement <var> pro cílovou proměnnou.
        var_el = self.generate_var(assignNode.varNode)
        assign_el.append(var_el)
        # Podelement <expr> pro výraz přiřazení.
        expr_el = self.generate_expr(assignNode.exprNode)
        assign_el.append(expr_el)
        return assign_el

    def generate_expr(self, exprNode) -> ET.Element:
        # Element <expr> – podle typu uzlu vygenerujeme jeden podelement.
        expr_el = ET.Element("expr")
        if isinstance(exprNode, AST.LiteralNode):
            literal_el = self.generate_literal(exprNode)
            expr_el.append(literal_el)
        elif isinstance(exprNode, AST.VarNode):
            var_el = self.generate_var(exprNode)
            expr_el.append(var_el)
        elif isinstance(exprNode, AST.BlockNode):
            block_el = self.generate_block(exprNode)
            expr_el.append(block_el)
        elif isinstance(exprNode, AST.ExprNode):
            send_el = self.generate_send(exprNode)
            expr_el.append(send_el)
        else:
            raise Exception("Neznámý typ výrazového uzlu.")
        return expr_el

    def generate_literal(self, literalNode: AST.LiteralNode) -> ET.Element:
        # Element <literal> s atributy class a value.
        attrib = {"class": literalNode.literalType, "value": str(literalNode.literalValue)}
        literal_el = ET.Element("literal", attrib=attrib)
        return literal_el

    def generate_var(self, varNode: AST.VarNode) -> ET.Element:
        # Pokud identifikátor začíná velkým písmenem, interpretujeme ho jako literál třídy.
        if varNode.id and varNode.id[0].isupper():
            attrib = {"class": "class", "value": varNode.id}
            return ET.Element("literal", attrib=attrib)
        else:
            attrib = {"name": varNode.id}
            return ET.Element("var", attrib=attrib)

    def generate_send(self, exprNode: AST.ExprNode) -> ET.Element:
        # Element <send> s atributem selector.
        attrib = {"selector": exprNode.selector}
        send_el = ET.Element("send", attrib=attrib)

        # Příjemce zprávy: přímo vygenerujeme element <expr> bez dalšího obalení.
        receiver_expr = self.generate_expr(exprNode.receiver)
        send_el.append(receiver_expr)

        # Pro každý argument zprávy vytvoříme element <arg> s atributem order.
        arg_order = 1
        for arg in exprNode.argNodeList:
            arg_el = ET.Element("arg", attrib={"order": str(arg_order)})
            # Přímo vygenerujeme element <expr> pro argument, bez dalšího obalení.
            arg_expr = self.generate_expr(arg)
            arg_el.append(arg_expr)
            send_el.append(arg_el)
            arg_order += 1

        return send_el


### konec souboru 'XMLGenerator.py' ###

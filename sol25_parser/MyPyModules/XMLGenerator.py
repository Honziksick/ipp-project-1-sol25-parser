"""
********************************************************************************
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           XMLGenerator.py                                            *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   24.02.2025                                                 *
*                                                                              *
* Popis:            Tento soubor obsahuje implementaci generátoru XML pro      *
*                   jazyk SOL25. Generátor prochází abstraktní syntaktický     *
*                   strom (AST) a vytváří XML reprezentaci programu.           *
********************************************************************************
"""

# Import modulů standardní knihovny
import re
from xml.dom import minidom
from xml.etree import ElementTree

# Import vlastních modulů
from MyPyModules.AbstractSyntaxTree import ASTNodes
from MyPyModules.CustomErrors import InternalError

#######################################################################
# Zdroje: https://www.datacamp.com/tutorial/python-xml-elementtree
#       : https://rowelldionicio.com/parsing-xml-with-python-minidom/
#######################################################################
class XMLGenerator:
    """
    Třída pro generování XML reprezentace programu v jazyce SOL25.

    Metody:
        - generate_XML(ASTRoot:ASTNodes.ProgramNode, SOL25Code:str) -> str:
            - Vytváří XML reprezentaci programu na základě AST a zdrojového kódu.

        - generate_class_tag(classNode:ASTNodes.ClassNode) -> ElementTree.Element:
            - Generuje element <class> pro uživatelsky definovanou třídu.

        - generate_method_tag(methodNode:ASTNodes.MethodNode) -> ElementTree.Element:
            - Generuje element <method> pro metodu třídy.

        - generate_block_tag(blockNode:ASTNodes.BlockNode) -> ElementTree.Element:
            - Generuje element <block> pro blok kódu.

        - generate_assign_tag(assignNode:ASTNodes.AssignNode) -> ElementTree.Element:
            - Generuje element <assign> pro přiřazení hodnoty proměnné.

        - generate_expression_tag(exprNode:ASTNodes) -> ElementTree.Element:
            - Generuje element <expr> pro výraz v kódu.

        - generate_literal_tag(literalNode: ASTNodes.LiteralNode) -> ElementTree.Element:
            - Generuje element <literal> pro literál v kódu.

        - generate_variable_tag(identifierNode: ASTNodes.IdentifierNode) -> ElementTree.Element:
            - Generuje element <var> pro proměnnou v kódu.

        - generate_send_tag(exprNode: ASTNodes.ExpressionNode) -> ElementTree.Element:
            - Generuje element <send> pro odeslání zprávy v kódu.
    """

    def generate_XML(self, ASTRoot:ASTNodes.ProgramNode, SOL25Code:str) -> str:
        """
        Generuje XML reprezentaci programu na základě abstraktního syntaktického
        stromu (AST).

        Parametry:
            - ASTRoot (ASTNodes.ProgramNode): Kořenový uzel AST.
            - SOL25Code (str): Zdrojový kód programu v jazyce SOL25.

        Návratová hodnota:
            - str: Hezky formátovaná XML reprezentace programu v SOL25.
        """
        # Vytvoříme slovník s atributy zdrojového kódu.
        attributes = {"language": "SOL25"}  # definice jazyka programu

        # Vyhledání prvního komentáře v kódu SOL25
        firstComment = get_first_comment(SOL25Code)

        # Pokud je nalezen komentář, přidáme ho jako atribut "description"
        if firstComment:
            description = firstComment
            attributes["description"] = description

        # Vygenerujeme element <program> s atributy do stromu elementů XML.
        programTag = ElementTree.Element("program", attributes)

        # Pro každou uživatelsky definovanou třídu vytvoříme element <class>.
        order = 1
        for classNode in ASTRoot.classNodeList:
            classTag = self.generate_class_tag(classNode)
            programTag.append(classTag)
            order += 1

        # Převod elementu XML na řetězec.
        byteXML = ElementTree.tostring(element=programTag, encoding="utf-8")

        # Převod řetězcové reprezentace XML na DOM objektovou reprezentaci.
        reparsedXML = minidom.parseString(byteXML)

        # Override funkce pro zápis hezky formátovaného XML, aby nedocházelo k escapování znaků.
        def no_escape_write_data(writer, data):
            writer.write(data)
        minidom._write_data = no_escape_write_data

        # Zdroj: https://rowelldionicio.com/parsing-xml-with-python-minidom/
        prettyXML = reparsedXML.toprettyxml(indent="  ", encoding="UTF-8")

        # Dekódování bajtového řetězce na textový řetězec.
        XMLCode = prettyXML.decode("UTF-8")
        return XMLCode

    def generate_class_tag(self, classNode:ASTNodes.ClassNode) -> ElementTree.Element:
        """
        Generuje XML element <class> pro daný uzel třídy. Každý element <class>
        obsahuje dva povinné atributy: `name` s identifikátorem třídy a `parent`
        s identifikátorem nadtřídy (rodiče).

        Parametry:
            - classNode (ASTNodes.ClassNode): Uzel třídy v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <class>.
        """
        # Atributem elementu třídy <class> je identifikátor třídy a identifikátor nadtřídy.
        attributes = {
            "name": classNode.identifier,
            "parent": classNode.perentIdentifier
        }

        # Přidáme element <class> s atributy do stromu elementů XML.
        classTag = ElementTree.Element("class", attributes)

        # Vygenerujeme elementy <method> pro každou definovanou metodu dané třídy.
        for methodNode in classNode.methodNodeList:
            methodTag = self.generate_method_tag(methodNode)
            classTag.append(methodTag)
        return classTag

    def generate_method_tag(self, methodNode:ASTNodes.MethodNode) -> ElementTree.Element:
        """
        Generuje XML element <method> pro daný uzel metody. Element <method>
        obsahuje povinný atribut `selector` s identifikátorem metody. Při
        generování některých elementů je třeba definovat pořadí, což se provádí
        povinným atributem `order`.

        Parametry:
            - methodNode (ASTNodes.MethodNode): Uzel metody v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <method>.
        """
        # Metoda je tvořena elementem <method> s atributem 'selector'.
        attributes = {"selector": methodNode.selector}

        # Vygenerujeme element <method> s atributy do stromu elementů XML.
        methodTag = ElementTree.Element("method", attributes)

        # Tělo metody je reprezentováno blokem.
        blockTag = self.generate_block_tag(methodNode.blockNode)
        methodTag.append(blockTag)
        return methodTag

    def generate_block_tag(self, blockNode:ASTNodes.BlockNode) -> ElementTree.Element:
        """
        Generuje XML element <block> pro daný uzel bloku. Element <block>
        obsahuje podelementy `parameter` pro každý parametr bloku se dvěma
        povinným atributy `order` a `name` pro pořadí a identifikátor parametru.
        Dále element <block> obsahuje podelementy pro každý příkaz sekvence
        příkazů a s atributem arity udávajícím počet očekávaných argumentů.

        Parametry:
            - blockNode (ASTNodes.BlockNode): Uzel bloku v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <block>.
        """
        # Zjistíme počet parametrů bloku, pokud je seznam parametrů prázdný, arita je 0.
        arity = len(blockNode.parameterNodeList) if blockNode.parameterNodeList else 0
        attributes = {"arity": str(arity)}

        # Vygenerujeme element <block> s atributy do stromu elementů XML.
        blockTag = ElementTree.Element("block", attributes)

        # Pro každý parametr bloku vytvoříme element <parameter> s atributy 'name' a 'order'.
        order = 1
        for param in blockNode.parameterNodeList:
            attributes = {"order": str(order),
                          "name": param
                          }
            parameterTag = ElementTree.Element("parameter", attributes)
            blockTag.append(parameterTag)
            order += 1

        # Pro každý příkaz přiřazení v bloku vytvoříme element <assign>.
        order = 1
        for statement in blockNode.statementNodeList:
            assignTag = self.generate_assign_tag(statement, order)
            blockTag.append(assignTag)
            order += 1
        return blockTag

    def generate_assign_tag(self, assignNode:ASTNodes.AssignNode, order:int) -> ElementTree.Element:
        """
        Generuje XML element <assign> pro příkaz. Element <assign> má povinný
        atribut `order` pro určení pořadí příkazu v sekvenci příkazů. Příkaz
        zahrnuje dva povinné podelementy `var` s atributem `name` pro identifikátor
        cílové proměnné a podelement `expr` pro výraz pro výpočet přiřazované hodnoty.

        Parametry:
            - assignNode (ASTNodes.AssignNode): Uzel příkazu (přiřazení) v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <assign>.
        """
        # Přidáme element příkazu <assign> do stromu elementů XML.
        attributes = {"order": str(order)}
        assignTag = ElementTree.Element("assign", attributes)

        # Vygenerujeme podelement <var> pro proměnnou, do které přiřazujeme.
        variableTag = self.generate_variable_tag(assignNode.identifierNode)
        assignTag.append(variableTag)

        # Vygenerujeme podelement <expr> pro výraz, který přiřazujeme.
        expressionTag = self.generate_expression_tag(assignNode.exprNode)
        assignTag.append(expressionTag)
        return assignTag

    def generate_expression_tag(self, exprNode:ASTNodes) -> ElementTree.Element:
        """
        Generuje XML element <expr> pro daný uzel výrazu. Výraz obsahuje jeden
        podelement podle druhu výrazu: (1) literál <literal>, (2) proměnná <var>,
        (3) blokový literál <block> nebo (4) zaslání zprávy <send>.

        Parametry:
            - exprNode (ASTNodes): Uzel výrazu v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <expr>.
        """
        # Přidáme element <expr>, který nemá atributy, do stromu elementů XML.
        expressionTag = ElementTree.Element("expr")

        # Podle typu uzlu vygenerujeme odpovídající podelement.
        if isinstance(exprNode, ASTNodes.LiteralNode):
            literalTag = self.generate_literal_tag(exprNode)  # literál Integer, String, True, False, Nil
            expressionTag.append(literalTag)
        elif isinstance(exprNode, ASTNodes.IdentifierNode):
            variableTag = self.generate_variable_tag(exprNode)  # proměnná | literál třídy
            expressionTag.append(variableTag)
        elif isinstance(exprNode, ASTNodes.BlockNode):
            blockTag = self.generate_block_tag(exprNode)  # zpracujeme blokový literál
            expressionTag.append(blockTag)
        elif isinstance(exprNode, ASTNodes.ExpressionNode):
            sendTag = self.generate_send_tag(exprNode)  # zpracujeme odeslání zprávy
            expressionTag.append(sendTag)
        else:
            raise InternalError(
                f"Uknown expression node type '{exprNode}' was detected while "
                f"generating XML output ."
            )
        return expressionTag

    def generate_literal_tag(self, literalNode: ASTNodes.LiteralNode) -> ElementTree.Element:
        """
        Generuje XML element <literal> pro daný uzel literálu. Element <literal>
        obsahuje dva povinné textové atributy `class` s identifikátorem vestavěné
        třídy (Integer/String/Nil/True/False) a atribut `value` reprezentující
        hodnotu literálu.

        Parametry:
            - literalNode (ASTNodes.LiteralNode): Uzel literálu v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <literal>.
        """
        # Atributem elementu literálu <liteal> je třída (typ) literálu a jeho hodnota.
        attributes = {"class": literalNode.literalType,
                      "value": str(literalNode.literalValue)
                      }
        # Vygenerujeme element <literal> do stromu elementů XML
        literalTag = ElementTree.Element("literal", attributes)
        return literalTag

    def generate_variable_tag(self, identifierNode: ASTNodes.IdentifierNode) -> ElementTree.Element:
        """
        Generuje XML element <var> nebo <literal> typu `class` pro daný uzel
        identifikátoru. Element <var> obsahuje povinný atribut `name` s
        identifikátorem proměnné. Pro vyjádření literálu identifikátoru
        třídy je `class="class"` a `value` obsahuje identifikátor třídy.

        Parametry:
            - identifierNode (ASTNodes.IdentifierNode): Uzel identifikátoru v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <var> nebo <literal>.
        """
        # Pokud identifikátor začíná velkým písmenem, interpretujeme ho jako literál třídy.
        if identifierNode.identifier and identifierNode.identifier[0].isupper():
            attributes = {"class": "class",
                          "value": identifierNode.identifier
                          }
            return ElementTree.Element("literal", attributes)
        # Jinak ho považujeme za identifikátor proměnné.
        else:
            attributes = {"name": identifierNode.identifier}
            return ElementTree.Element("var", attributes)

    def generate_send_tag(self, exprNode: ASTNodes.ExpressionNode) -> ElementTree.Element:
        """
        Generuje XML element <send> pro daný uzel odeslání zprávy. Selektor
        zprávy je uložen v povinném atributu `selector`. Výraz pro vyhodnocení
        příjemce je v podelementu <expr> a pokud se jedná o parametrickou zprávu,
        obsahuje element <send> ještě podelementy <arg> pro každý argument
        předávaný zprávě. Element <arg> obsahuje právě jeden podelement <expr>
        pro výraz, jehož vyhodnocením získáme skutečný argument zprávy.

        Parametry:
            - exprNode (ASTNodes.ExpressionNode): Uzel odeslání zprávy v AST.

        Návratová hodnota:
            - ElementTree.Element: XML element <send>.
        """
        # Atributem elementu zprávy <send> je selektor odesílatele zprávy.
        attributes = {"selector": exprNode.selector}

        # Vygenerujeme element <send> do stromu elementů XML.
        sendTag = ElementTree.Element("send", attributes)

        # Příjemcem zpárvy je výraz s elementem <expr>.
        receiverExpression = self.generate_expression_tag(exprNode.receiver)
        sendTag.append(receiverExpression)

        # Pro každý argument zprávy vytvoříme element <arg> s atributem `order`.
        order = 1
        for argument in exprNode.argNodeList:
            # Vygenerujeme element <arg> pro argument do stromu elementů XML.
            attributes = {"order": str(order)}
            argumentTag = ElementTree.Element("arg", attributes)
            # Vygenerujeme element <expr> pro výraz argumentu.
            argumentExpression = self.generate_expression_tag(argument)
            argumentTag.append(argumentExpression)
            sendTag.append(argumentTag)  # přidáme argument do zprávy
            order += 1
        return sendTag

def get_first_comment(SOL25Code:str) -> str | None:
    """
    Vyhledá první komentář v kódu SOL25.

    Parametry:
        - SOL25Code (str): Zdrojový kód programu v jazyce SOL25.

    Návratová hodnota:
        - str: První nalezený komentář nebo None, pokud není nalezen.
    """
    # Vyhledání prvního komentáře v kódu SOL25
    match = re.search(r'"(.*?)"', SOL25Code, re.DOTALL)
    if match:
        firstComment = match.group(0)
        return firstComment.strip("\"").replace("\n", "&nbsp;")
    else:
        return None

### konec souboru 'XMLGenerator.py' ###

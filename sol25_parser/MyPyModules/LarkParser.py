"""
********************************************************************************
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           LarkParser.py                                              *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   23.02.2025                                                 *
*                                                                              *
* Popis:            Tento soubor obsahuje implementaci parseru pro jazyk       *
*                   SOL25 pomocí knihovny Lark. Parser zahrnuje definici       *
*                   gramatiky, transformace parse stromu na abstraktní         *
*                   syntaktický strom (AST) a zpracování chyb.                 *
********************************************************************************
"""

# Import modulů standardní knihovny
from typing import Any, List

# Import modulů instalovaných pomocí 'pip'
from lark import Lark, Transformer, UnexpectedCharacters, UnexpectedToken, visitors

# Import vlastních modulů
from MyPyModules.AbstractSyntaxTree import ASTNodes
from MyPyModules.CustomErrors import InternalError, LexicalError, SyntacticError

################################################################################
#                                                                              #
#                NĚKOLIK SPECIFIK ZÁPISU PARSERU V MODULU "lark"               #
#                  Zdroj (manuál): lark-parser.readthedocs.io                  #
#                                                                              #
################################################################################
# ==============================================================================
# Konvence: gramatika je definována jako hodnota KONSTANTY
#         : Terminály (tokeny) se zapisují velkými písmeny (v lark.Lark)
#         : NEterminály se zapisují písmeny písmeny (v lark.Lark)
#         : metody v lark.Transformer musí být pojmenovány stejně jako
#           neterminál na levé straně pravidla, popř. terminál
#         : u pravidla s více různými možnými pravými stranami oddělujeme
#           pravé strany promocí '|'
#         : uvnitř konstanty s gramatikou lze psát jednořádkové komentář
#           uvzoené pomocí '//'
#         : vyhazuje dva typy vyjímek 'UnexpectedCharacters' a 'UnexpectedToken'
# ==============================================================================
# _TERMINAL: ...   hodnota tokenu se neuloží do ParseTree díky prefixu '_'
# ?non_term: ...   operátor '?' nevloží uzel pro toto pravidlo do ParseTree
# X*               0 nebo více opakování X
# X+               1 nebo více opakování X
# X?               nanejvýš jednou (0 nebo 1 výskyt X), náhrada ε-pravidla
# (X Y)*           0 nebo více opakování X Y
# (X Y)+           1 nebo více opakování X Y
# (X Y)?           nanejvýš jednou (0 nebo 1 výskyt X Y), náhrada ε-pravidla
# (Keyword | Id)   POZOR, vyhodnocuje se zleva => 'Keyword' má vyšší prioritu
# %ignore cokoliv  změní význam 'cokoliv' na bílý znak a při parsování odignoruje
# ==============================================================================

# Konstanta obsahující definici gramatiky, lexikálních a syntaktických pravidel SOL25
SOL25_GRAMMAR = r"""
    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                   TERMINÁLY (tokeny) V JAZYCE SOL25                    //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Klíčová slova
    _CLASS: "class"
    SELF:   "self"
    SUPER:  "super"
    NIL:    "nil"
    TRUE:   "true"
    FALSE:  "false"

    // Speciální znaky
    _COLON:                ":"
    _SEMICOLON:            ";"
    _LEFT_ROUND_BRACKET:   "("
    _RIGHT_ROUND_BRACKET:  ")"
    _LEFT_CURLY_BRACKET:   "{"
    _RIGHT_CURLY_BRACKET:  "}"
    _LEFT_SQUARE_BRACKET:  "["
    _RIGHT_SQUARE_BRACKET: "]"
    _PIPE:                 "|"
    _DOT:                  "."

    // Operátory
    _WALRUS: ":="

    // Literály
    INT_LITERAL:    /[+-]?\d+/
    STRING_LITERAL: /'(\\(?:[n'\\])|[^'\\])*'/

    // Identifikátory
    ID:          /[a-z_][A-Za-z0-9_]*/
    ID_SELECTOR: /[a-z_][A-Za-z0-9_]*:/
    SELECTOR_ID: /:[a-zA-Z_][A-Za-z0-9_]*/
    CID:         /[A-Z][A-Za-z0-9]*/



    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                   GRAMATICKÁ PRAVIDLA V JAZYCE SOL25                   //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Startovacím pravidlem je "program"
    ?start: program


    // =============================
    // Základní struktura programu
    // =============================

    // Program -> Class Program | ε
    program: (class_definition)*

    // Class -> class <Cid> : <Cid> { Method }
    class_definition: _CLASS CID _COLON CID _LEFT_CURLY_BRACKET method_definition _RIGHT_CURLY_BRACKET

    // Method -> Selector Block Method | ε
    method_definition: (selector block)*


    // ==============================
    // Selektory při definici metod
    // ==============================

    // Selector -> <identifier> | <identifier:> SelectorTail
    selector: ID
            | ID_SELECTOR selector_tail

    // SelectorTail -> <identifier:> SelectorTail | ε
    selector_tail: (ID_SELECTOR)*


    // =======
    // Bloky
    // =======

    // Block -> [ BlockPar | BlockStat ]
    block: _LEFT_SQUARE_BRACKET block_parameter _PIPE block_statement _RIGHT_SQUARE_BRACKET

    // BlockPar -> <:identifier> BlockPar | ε
    block_parameter: (SELECTOR_ID)*

    // BlockStat -> <identifier> := Expr . BlockStat | ε
    block_statement: (ID _WALRUS expression _DOT)*


    // =========================
    // Výrazy a zasílání zpráv
    // =========================

    // Expr -> ExprBase ExprTail
    expression: expression_base expression_tail

    // ExprTail -> <identifier> | ExprSel
    expression_tail: ID
                   | expression_selector

    // ExprSel -> <identifier:> ExprBase ExprSel | ε
    expression_selector: (ID_SELECTOR expression_base)*

    // ExprBase -> <int> | <str> | <identifier> | <Cid> | Block | ( Expr )
    expression_base: INT_LITERAL
                   | STRING_LITERAL
                   | NIL
                   | TRUE
                   | FALSE
                   | SELF
                   | SUPER
                   | CID
                   | block
                   | _LEFT_ROUND_BRACKET expression _RIGHT_ROUND_BRACKET
                   | ID


    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                 KOMENTÁŘE A BÍLÉ ZNAKY V JAZYCE SOL25                  //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Komentáře
    COMMENT: /"[^"]*"/
    %ignore COMMENT

    // Bílé znaky
    %import common.WS
    %ignore WS
"""


# Zdroj (manuál): lark-parser.readthedocs.io/en/stable/visitors.html
# noinspection PyMethodMayBeStatic
class LarkTransformer(Transformer):
    """
    Třída `LarkTransformer` transformuje výstupní parse strom modulu 'lark' na
    abstraktní syntaktický strom (AST).

    Metody:
        - __init__():                Inicializuje instanci třídy `LarkTransformer`.
        - program(args):             Transformuje pravidlo 'program' na uzel AST.
        - class_definition(args):    Transformuje pravidlo 'class_definition' na uzel AST.
        - method_definition(args):   Transformuje pravidlo 'method_definition' na seznam uzlů AST.
        - selector(args):            Transformuje pravidlo 'selector' na řetězec nebo kombinaci řetězců.
        - selector_tail(args):       Transformuje pravidlo 'selector_tail' na seznam řetězců.
        - block(args):               Transformuje pravidlo 'block' na uzel AST.
        - block_parameter(args):     Transformuje pravidlo 'block_parameter' na seznam řetězců.
        - block_statement(args):     Transformuje pravidlo 'block_statement' na seznam uzlů AST.
        - expression(args):          Transformuje pravidlo 'expression' na uzel AST.
        - expression_tail(args):     Transformuje pravidlo 'expression_tail' na řetězec nebo seznam.
        - expression_selector(args): Transformuje pravidlo 'expression_selector' na seznam.
        - expression_base(args):     Transformuje pravidlo 'expression_base' na uzel AST.
        - INT_LITERAL(token):        Vytvoří uzel AST pro literál typu Integer.
        - STRING_LITERAL(token):     Vytvoří uzel AST pro literál typu String.
        - NIL(token):                Vytvoří uzel AST pro literál typu Nil.
        - TRUE(token):               Vytvoří uzel AST pro literál typu Bool s hodnotou 'true'.
        - FALSE(token):              Vytvoří uzel AST pro literál typu Bool s hodnotou 'false'.
        - SELF(token):               Vytvoří uzel AST pro proměnnou 'self'.
        - SUPER(token):              Vytvoří uzel AST pro proměnnou 'super'.
        - ID(token):                 Vrátí identifikátor <id> a zkontroluje jeho platnost.
        - ID_SELECTOR(token):        Vrátí identifikátor <id:> a zkontroluje jeho platnost.
        - SELECTOR_ID(token):        Vrátí identifikátor <:id> a zkontroluje jeho platnost.
        - CID(token):                Vrátí identifikátor třídy <Cid> a zkontroluje jeho platnost.

    Parametry metod:
        - args (list): Seznam argumentů vytvořený parsováním daného pravidla.
        - token (Token): Token reprezentující daný terminál.

    Návratové hodnoty:
        - str: Řetězce reprezentující indetifikátory či selektory.
        - ASTNodes: Specifický uzel AST, který je výsledkem daného pravidla.
        - list: Seznamy řetězců (str) nebo specifických uzlů AST (ASTNodes).
    """

    def __init__(self):
        """
        Inicializuje instanci třídy `LarkTransformer`.

        Atributy:
            - _keywords (set): Množina klíčových slov jazyka SOL25.
        """
        super().__init__()
        self._keywords = {"class", "self", "super", "nil", "true", "false"}
        self._reserved_words = {"Main", "run"}


    #######################################
    # Transformace pravidel (NEterminálů)
    #######################################

    def program(self, args) -> ASTNodes.ProgramNode:
        """
        Program -> Class Program | ε
        """
        return ASTNodes.ProgramNode(args)

    def class_definition(self, args) -> ASTNodes.ClassNode:
        """
        Class ->  class   <Cid>   :   <Cid>    {   Method   }
        Class ->         args[0]     args[1]       args[2]
        """
        # args = [<Cid>, <Cid>, Method]
        classIdentifier = str(args[0])
        parentClass     = str(args[1])
        classMethodList = args[2] if len(args) > 2 else []

        # Raději zajístíme, že výstupem args[2] je skutečně seznam metod
        if not isinstance(classMethodList, list):
            classMethodList = [classMethodList]
        return ASTNodes.ClassNode(classIdentifier, parentClass, classMethodList)

    def method_definition(self, args) -> List[ASTNodes.MethodNode]:
        """
        Method ->  Selector   Block    Method | ε
        Method ->  args[2k] args[2k+1]
        """
        # args = [selector1, blockNode1, selector2, blockNode2, ..., selectorN, blockNodeN]
        methodList = []
        for i in range(0, len(args), 2):
            methodSelector = args[i]  # args[2k]
            methodBlock = args[i + 1]  # args[2k+1]
            methodList.append(ASTNodes.MethodNode(methodSelector, methodBlock))
        return methodList

    def selector(self, args) -> str:
        """
        Selector -> <id> |  <id:>  SelectorTail
        Selector -> args | args[0]   args[1]
        """
        # Bezparametrický selektor '<id>' (tj. `args` není seznam)
        if len(args) == 1:
            return str(args[0])  # vracíme `args` jako řetězec

        # Parametrický selektor '<id:>' (tj. `args` je seznam)
        # args = [selector, [selector_tail]]
        else:
            selectorHead = str(args[0])  # první selektor
            selectorTail = "".join(args[1])  # seznam dalších slektorů
            return selectorHead + selectorTail

    def selector_tail(self, args) -> List[str]:
        """
        SelectorTail -> <id:> SelectorTail | ε
        """
        # Raději zajístíme, že `args` je skutečně seznamem selektorů
        if not isinstance(args, list):
            args = [args]
        return [str(selector) for selector in args]

    def block(self, args) -> ASTNodes.BlockNode:
        """
        Block -> [ BlockPar | BlockStat ]
        """
        blockParameterList = args[0] if len(args) > 0 else []
        blockStatementList = args[1] if len(args) > 1 else []
        return ASTNodes.BlockNode(blockParameterList, blockStatementList)

    def block_parameter(self, args) -> List[str]:
        """
        BlockPar -> <:id> BlockPar | ε
        """
        # Raději zajístíme, že `args` je skutečně seznamem selektorů
        if not isinstance(args, list):
            args = [args]
        return [str(selector) for selector in args]

    def block_statement(self, args) -> List[ASTNodes.AssignNode]:
        """
        BlockStat ->   <id>   :=    Expr    . BlockStat | ε
        BlockStat -> args[2k]    args[2k+1]
        """
        # args = [<id>1, Expr1, <id>, Expr2, ..., <id>N, ExprN]
        blockStatementList = []
        for i in range(0, len(args) - 1, 2):
            assignToVariable = args[i]      # args[2k]   -> str
            expression       = args[i + 1]  # args[2k+1] -> Any
            variableNode     = ASTNodes.IdentifierNode(str(assignToVariable))
            assignNode       = ASTNodes.AssignNode(variableNode, expression)
            blockStatementList.append(assignNode)
            if variableNode.identifier in self._reserved_words:
                raise SyntacticError(f"Identifier can't be reserved word '{assignToVariable}'.")
        return blockStatementList

    def expression(self, args) -> ASTNodes.ExpressionNode | None:
        """
        Expr -> ExprBase  ExprTail
        Expr ->  args[0]   args[1]
        """
        expressionBase = args[0]
        if len(args) == 1:
            return expressionBase
        else:
            expressionTail = args[1]
            # Buď je `expressionTail` jednoduché volání metody bez argumentů (tj. řetězec)
            if isinstance(expressionTail, str) and len(expressionTail) > 0:
                return ASTNodes.ExpressionNode(expressionBase, expressionTail, [])
            # Nebo je `expressionTail` seznam ve tvaru [<id:>1, ExprBase1, ..., <id:>N, ExprBaseN]
            elif isinstance(expressionTail, list):
                if len(expressionTail) == 0:
                    return expressionBase

                # Vytváříme zasílání zprávy tak, že "posbíráme" selektory a argumenty.
                selectors = []
                args = []
                for i in range(0, len(expressionTail), 2):
                    selectors.append(str(expressionTail[i]))
                    args.append(expressionTail[i + 1])

                # Konkatenace selektorů do jednoho řetězce
                concatenated = "".join(selectors)

                if ((isinstance(expressionBase, ASTNodes.LiteralNode) or
                    isinstance(expressionBase, ASTNodes.IdentifierNode) or
                    isinstance(expressionBase, ASTNodes.BlockNode)) and
                    len(concatenated) == 0
                   ):
                    return expressionBase
                else:
                    return ASTNodes.ExpressionNode(expressionBase, concatenated, args)

            # Pro neočekávané hodnoty (ani str, ani list) vyhodíme výjimku
            else:
                raise InternalError(f"While transforming 'expression', unexpected variable was "
                                    f"created. Type: {type(expressionTail)}, Value: {expressionTail}"
                                    )

    def expression_tail(self, args) -> Any:
        """
        ExprTail -> <id> | ExprSel
        """
        return args[0]

    def expression_selector(self, args) -> List[str | Any]:
        """
        ExprSel ->  <id:>    ExprBase    ExprSel | ε
        ExprSel -> args[2k] args[2k+1]
        """
        # args = [<id:>1, ExprBase1, <id:>, ExprBase2, ..., <id:>N, ExprBaseN]
        expressionSelector = []
        for i in range(0, len(args), 2):
            expressionSelector.append(str(args[i]))
            expressionSelector.append(args[i + 1])
        return expressionSelector

    def expression_base(self, args) -> ASTNodes:
        """
        ExprBase -> <int> | <str> | <id> | <Cid> | Block | ( Expr )
        """
        if isinstance(args[0], str):
            if args[0] in self._reserved_words:
                raise SyntacticError(f"Identifier can't be reserved word '{args[0]}'.")
            else:
                return ASTNodes.IdentifierNode(args[0])  # <id> | <Cid>
        else:
            return args[0]  # <int> | <str> | Block | ( Expr )

    ###################################
    # Transformace tokenů (terminálů)
    ###################################

    def INT_LITERAL(self, token) -> ASTNodes.LiteralNode:
        """
        Vytvoří uzel AST pro literál typu Integer.
        """
        return ASTNodes.LiteralNode("Integer", int(token))

    def STRING_LITERAL(self, token) -> ASTNodes.LiteralNode:
        """
        Vytvoří uzel AST pro literál typu String.
        """
        value = str(token)
        # Provedeme úpravy hodnoty literálu kvůli následné XML reprezentaci.
        modifiedValue = (value.strip("'")
                            .replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                            .replace("'", "&apos;")
                            .replace('"', "&quot;"))
        return ASTNodes.LiteralNode("String", modifiedValue)

    def NIL(self, token) -> ASTNodes.LiteralNode:
        """
        Vytvoří uzel AST pro literál typu Nil.
        """
        return ASTNodes.LiteralNode("Nil", "nil")

    def TRUE(self, token) -> ASTNodes.LiteralNode:
        """
        Vytvoří uzel AST pro literál typu bool s hodnotou 'true'.
        """
        return ASTNodes.LiteralNode("True", "true")

    def FALSE(self, token) -> ASTNodes.LiteralNode:
        """
        Vytvoří uzel AST pro literál typu bool s hodnotou 'false'.
        """
        return ASTNodes.LiteralNode("False", "false")

    def SELF(self, token) -> ASTNodes.IdentifierNode:
        """
        Vytvoří uzel AST pro pseudoproměnnou `self`.
        """
        return ASTNodes.IdentifierNode("self")

    def SUPER(self, token) -> ASTNodes.IdentifierNode:
        """
        Vytvoří uzel AST pro pseudoproměnnou `super`.
        """
        return ASTNodes.IdentifierNode("super")

    def ID(self, token) -> str:
        """
        Vrátí identifikátor <id> a zkontroluje, že se nejedná o klíčové slovo.
        """
        identifier = str(token)
        if identifier in self._keywords:
            raise SyntacticError(f"Identifier can't be keyword '{identifier}'.")
        return identifier

    def ID_SELECTOR(self, token) -> str:
        """
        Vrátí identifikátor z původního tokenu <id:> a zkontroluje,
        že se nejedná o klíčové slovo.
        """
        identifier = str(token)

        return identifier

    def SELECTOR_ID(self, token) -> str:
        """
        Vrátí identifikátor z původního tokenu <:id> a zkontroluje,
        že se nejedná o klíčové slovo. Identifikátor je vrácen bez uvozující dvojtečky.
        """
        identifier = str(token)[1:]
        if identifier in self._keywords or identifier in self._reserved_words:
            raise SyntacticError(f"Selector can't be keyword '{identifier}'.")
        return identifier

    def CID(self, token) -> str:
        """
        Vrátí identifikátor třidy <Cid> a zkontroluje, že se nejedná
        o klíčové slovo.
        """
        identifier = str(token)
        if identifier in self._keywords:
            raise SyntacticError(f"Class identifier can't be keyword '{identifier}'.")
        return identifier


class LarkParser:
    """
    Třída `LarkParser` je zodpovědná za parsování kódu v jazyce SOL25 pomocí
    knihovny Lark. Převádí parsovaný kód na abstraktní syntaktický strom (AST)
    pomocí třídy `LarkTransformer`.

    Atributy:
        - _larkParser (Lark): Instance 'Lark' parseru inicializovaná gramatikou SOL25.
        - _ASTBuilder (LarkTransformer): Instance třídy LarkTransformer pro
                                         transformaci parse stromu na AST.
    """

    def __init__(self):
        self._larkParser = Lark(SOL25_GRAMMAR, parser = "lalr", start = "start")
        self._ASTBuilder = LarkTransformer()

    def parse_code(self, SOL25Code) -> ASTNodes.ProgramNode:
        """
        Parsuje zadaný kód v jazyce SOL25 a převádí jej na abstraktní
        syntaktický strom (AST).

        Parametry:
            - SOL25Code (str): Kód v jazyce SOL25, který má být parsován.

        Návratová hodnota:
            - ASTNodes.ASTProgram: Kořenový uzel vygenerovaného AST.

        Výjimky:
            - LexicalError: Pokud se v kódu vyskytují neočekávané znaky.
            - SyntacticError: Pokud se v kódu vyskytují neočekávané tokeny.
            - Exception: Pro jakékoli jiné výjimky, které nastanou během
                         parsování nebo transformace.
        """
        # Parsování kódu SOL25 a generování lark parse stromu
        try:
            larkParseTree = self._larkParser.parse(SOL25Code)
        except UnexpectedCharacters as e:
            raise LexicalError() from e
        except UnexpectedToken as e:
            raise SyntacticError() from e
        except Exception:
            raise

        # Transformace lark parse stromu na abstraktní syntaktický strom (AST)
        try:
            ASTRoot = self._ASTBuilder.transform(larkParseTree)
            return ASTRoot
        # Pokud během transofrmace selhala kontrola regulárním výrazem
        except visitors.VisitError as e:
            raise SyntacticError(str(e.orig_exc.errorDetail)) from e
        # Pokud během transformace došlo k jakékoliv jiné chybě
        except Exception:
            raise

### konec souboru 'LarkParser.py' ###


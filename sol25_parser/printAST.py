from rich.tree import Tree
from rich import print
from MyPyModules.AbstractSyntaxTree import ASTNodes

class ASTVisualizer:
    def visit_program_node(self, node):
        tree = Tree("[bold blue]Program")
        for class_node in node.classNodeList:
            tree.add(self.visit_class_node(class_node))
        return tree

    def visit_class_node(self, node):
        class_tree = Tree(f"[bold magenta]Class: {node.identifier}[/bold magenta] (extends {node.perentIdentifier})")
        for method in node.methodNodeList:
            class_tree.add(self.visit_method_node(method))
        return class_tree

    def visit_method_node(self, node):
        method_tree = Tree(f"[bold cyan]Method: {node.selector}[/bold cyan]")
        method_tree.add(self.visit_block_node(node.blockNode))
        return method_tree

    def visit_block_node(self, node):
        block_tree = Tree(f"[bold yellow]Block[/bold yellow]")
        for param in node.parameterNodeList:
            block_tree.add(self.visit_identifier_node(param))
        for statement in node.statementNodeList:
            block_tree.add(self.visit_statement(statement))
        return block_tree

    def visit_identifier_node(self, node):
        return Tree(f"[green]Identifier: {node.identifier}[/green]")

    def visit_literal_node(self, node):
        return Tree(f"[red]Literal ({node.literalType}): {node.literalValue}[/red]")

    def visit_assign_node(self, node):
        assign_tree = Tree("[bold white]Assignment[/bold white]")
        assign_tree.add(self.visit_identifier_node(node.identifierNode))
        assign_tree.add(self.visit_statement(node.exprNode))
        return assign_tree

    def visit_expression_node(self, node):
        expr_tree = Tree(f"[bold blue]Expression: {node.selector}[/bold blue]")
        expr_tree.add(self.visit_statement(node.receiver))
        for arg in node.argNodeList:
            expr_tree.add(self.visit_statement(arg))
        return expr_tree

    def visit_statement(self, node):
        return node.visit_by(self)  # Dynamické volání podle typu uzlu

# Testovací AST
program = ASTNodes.ProgramNode([
    ASTNodes.ClassNode("Main", "Object", [
        ASTNodes.MethodNode("run", ASTNodes.BlockNode([], [
            ASTNodes.AssignNode(ASTNodes.IdentifierNode("x"), ASTNodes.LiteralNode("int", 42)),
            ASTNodes.ExpressionNode(ASTNodes.IdentifierNode("x"), "print", [])
            ]))
        ])
    ])



# Import modulů standardní knihovny
import sys  # exit(), stdin.read(), stderr

# Import vlastních modulů
from MyPyModules import CustomErrors as Error
from MyPyModules.ArgumentParser import ArgumentParser
from MyPyModules.LarkParser import LarkParser
from MyPyModules.SemanticAnalyser import SemanticAnalyser
from MyPyModules.XMLGenerator import XMLGenerator

################################################################################
#                                                                              #
#                     FASÁDA SKRIPTU 'parse.py' (PRIVÁTNÍ)                     #
#                                                                              #
################################################################################

class Facade:
    """
    Třída inspirovaná návrhovým vzorem "fasáda" pro analyzátor kódu v SOL25.
    Tato třída poskytuje jednotné rozhraní pro provádění syntaktické a
    sémantické analýzy zdrojového kódu v SOL25 a generování XML výstupu.

    Atributy:
        - _code (str):                 Zdrojový kód v SOL25.
        - _parser (LarkParser):        Instance parseru pro lexikální a syntaktickou analýzu.
        - _checker (SemanticAnalyser): Instance analyzátoru pro sémantickou analýzu.
        - _generator (XMLGenerator):   Instance generátoru XML výstupu.

    Metody: __init__(SOL25Code:str), run_analysis()
    """
    def __init__(self, SOL25Code):
        """
        Inicializuje fasádu se zdrojovým kódem v SOL25 předaným na STDIN.

        Parametry:
            - SOL25Code (str): Zdrojový kód v SOL25.
        """
        self._code = SOL25Code
        self._parser = LarkParser()
        self._checker = SemanticAnalyser()
        self._generator = XMLGenerator()

    def run_analysis(self):
        """
        Provede lexikální a syntaktickou analýzu zdrojového kódu v SOL25,
        sémantickou analýzu a generování XML výstupu.
        """
        # Provede lexikální a syntaktickou analýzu, jejímž výstupem je kořen
        # abstraktního syntaktického stromu (AST) reprezentující kód v SOL25.
        try:
            ASTRoot = self._parser.parse_code(self._code)
        except:
            raise

        # Provede sémantickou analýzu zdrojového kódu v SOL25
        try:
            self._checker.analyse_semantic(ASTRoot)
            vizaulizer = ASTVisualizer()
            tree = vizaulizer.visit_program_node(ASTRoot)
            print(tree)
        except:
            raise

        # Generování XML výstup na základě předaného kořenu AST
        try:
            XMLcode = self._generator.generate_XML(ASTRoot, self._code)
        except:
            raise

        # Pokud analýzu a generování kódu proběhlo úspěšně, vytiskne XML na STDOUT
        try:
            print(XMLcode)
        except:
            raise


################################################################################
#                                                                              #
#                  HLAVNÍ FUNKCE SKRIPTU 'parse.py' (VEŘEJNÉ)                  #
#                                                                              #
################################################################################

def main():
    """
    Hlavní funkce skriptu. Zpracovává argumenty příkazové řádky, načítá
    zdrojový kód ze STDIN a provádí analýzu kódu.
    """
    try:
        # Instanciace parseru vstupních argumentů a jejich zpracování
        argParser = ArgumentParser()
        try:
            argParser.parse_arguments()
        except:
            raise

        # Načtení zdrojového kódu v SOL25 ze STDIN
        try:
            SOL25Code = sys.stdin.read()
            if not SOL25Code:
                raise Error.InputFileError()
        except OSError:
            raise Error.InputFileError()

        # Instanciace fasády parseru 'parse.py'
        facade = Facade(SOL25Code)

        # Provedeme analýzu zrojového kódu SOL25
        try:
            facade.run_analysis()
        except:
            raise
    except:
        raise

    # Skript skončil úspěchem
    sys.exit(Error.ExitCode.SUCCESS.value)

if __name__ == "__main__":
    # Spuštění hlavní funkce skriptu
    try:
        main()
    # Zpracování jakýchkoli neočekávaných výjimek
    except Exception as e:
        Error.handle_exception(e)

### konec souboru 'parse.py' ###

# Implementační dokumentace `parse.py` a modulů MyPyModules

## Architektura a objektový návrh

Projekt `parse.py` je navržen modulárně a **objektově orientovaně**. Hlavní skript `parse.py` slouží jako vstupní bod – načítá zdrojový kód jazyka
SOL25 ze standardního vstupu, zpracuje argumenty příkazové řádky a spouští analýzu kódu. Samotná logika analýzy je však rozdělena do specializovaných
tříd v balíčku `MyPyModules`. Každá část zpracování má svou komponentu: syntaktickou a lexikální analýzu zajišťuje třída `LarkParser`, sémantickou
analýzu třída `SemanticAnalyser` a generování výstupu ve formátu XML třída `XMLGenerator`. Toto rozdělení odpovídá principu **jednotné 
odpovědnosti** – každá třída má jasně vymezenou funkci. Díky objektovému návrhu mohou tyto komponenty spolupracovat prostřednictvím dobře 
definovaných rozhraní.
Celková architektura tak zůstává přehledná a jednotlivé části je možné vyvíjet a testovat izolovaně.

## Návrhový vzor *Fasáda* v `parse.py`

V souboru `parse.py` je implementována třída **`Facade`**, inspirovaná návrhovým vzorem *fasáda*. Jejím úkolem je poskytnout jednotné rozhraní pro
celý proces analýzy zdrojového kódu. Třída `Facade` zapouzdřuje vytvoření a použití výše zmíněných komponent analyzátoru: v konstruktoru si připraví
instanci `LarkParser`, `SemanticAnalyser` a `XMLGenerator`. Navenek pak nabízí jednoduchou metodu `run_analysis()`, která postupně provede všechny
fáze analýzy – od parsování kódu, přes sémantickou kontrolu, až po generování XML. Hlavní funkce skriptu tak může analyzovat kód jediným voláním
`facade.run_analysis()`, aniž by se starala o detaily implementace jednotlivých kroků. Tento **fasádní přístup** zjednodušuje komunikaci se složitým
podsystémem: skrývá vnitřní složitost analýzy za jednoduché rozhraní. Přínosem je menší provázanost komponent – změny v interní logice (například
úprava formátu XML nebo vylepšení kontroly) nevyžadují úpravy v kódu, který fasádu využívá. Fasáda tak zlepšuje **udržovatelnost** a srozumitelnost
celého projektu, protože odděluje *co* se dělá (analýza kódu) od *jak* se to uvnitř provádí.

## Reprezentace AST a návrhový vzor *Visitor*

Po syntaktickém zpracování vstupního kódu generuje parser abstraktní syntaktický strom (AST) složený z objektů představujících konstrukce jazyka (uzly
pro program, třídy, metody, bloky, literály, proměnné atd.). Pro průchod tímto stromem a provedení sémantické analýzy byl použit návrhový vzor *
*Visitor (Návštěvník)**. V projektu je definováno rozhraní návštěvníka jako abstraktní třída `ASTNodeVisitor`. Tato třída deklaruje metody jako
`visit_program_node`, `visit_class_node`, `visit_method_node` a další pro každý typ uzlu v AST. **Dědičnost** a **překrývání (override)** zde hrají
klíčovou roli – třída `ASTNodeVisitor` poskytuje výchozí implementace (které vyvolají chybu, pokud nejsou překryty), a konkrétní návštěvník pro
sémantickou analýzu, třída `SemanticAnalyser`, z ní **dědí**. `SemanticAnalyser` tak **překrývá** všechny potřebné metody `visit_*_node` vlastní
implementací kontrol sémantiky. Například implementuje `visit_class_node(self, node)`, kde ověřuje pravidla pro třídy, a podobně `visit_method_node`,
`visit_expression_node` atd., pro kontrolu správnosti definic metod, výrazů či přiřazení.

Samotné uzly AST jsou navrženy tak, aby spolupracovaly s návštěvníkem. Každá třída uzlu (např. `ProgramNode`, `ClassNode`, `BlockNode`...) dědí ze
společné abstraktní třídy (v kódu označené jako `ASTAbstractNode`) a definuje metodu `visit_by(self, visitor)`. Tato metoda zavolá odpovídající funkci
návštěvníka – například `ProgramNode.visit_by` interně volá `visitor.visit_program_node(self)`. Tím je dosaženo dvojího dispatchingu: konkrétní typ
uzlu rozhodne, kterou metodu návštěvníka spustit. **Polymorfismus** zde umožňuje, že volání `someNode.visit_by(analyser)` automaticky vybere správnou
implementaci podle typu `someNode` (program, třída, výraz, ...), aniž by analýza musela ručně zjišťovat typ uzlu.

Využití vzoru *Visitor* výrazně přispívá k **oddělení logiky** od datové struktury. AST uzly pouze nesou data (např. seznam metod, jméno třídy atd.),
ale neřeší, jaké kontroly se nad nimi provádějí – to je úlohou návštěvníka. `SemanticAnalyser` tak obsahuje veškerou logiku sémantické analýzy na
jednom místě, což zlepšuje čitelnost a usnadňuje údržbu. Přidání nové kontroly nebo úprava pravidel se projeví úpravou kódu návštěvníka, zatímco
struktura AST může zůstat beze změny. Stejně tak lze snadno doplnit další návštěvníky (například pro různé analýzy či transformace), protože stačí
vytvořit novou třídu **dědící** z `ASTNodeVisitor` a implementovat požadované `visit_*` metody. Tento přístup demonstruje flexibilitu objektového
návrhu: rozšiřování funkcionality skrze dědičnost namísto úprav existujícího kódu.

## Další prvky dědičnosti v návrhu

Návrh využívá dědičnost i mimo samotný vzor Visitor. Všechny třídy uzlů AST sdílejí společného předka (`ASTAbstractNode`), což zajišťuje konzistentní
rozhraní (`visit_by`) pro průchod stromem a případně možnost doplnit společné funkcionality pro uzly. Podobně je řešen i systém chyb: vlastní výjimky
definované v modulu `CustomErrors` tvoří hierarchii, kde specifické chyby (např. `InputFileError` pro chybu vstupu nebo `SemanticMainRunError` pro
chybějící metodu `run`) **dědí** od společných předků. To umožňuje jednotné zachytávání a zpracování výjimek v celém projektu (ve skriptu `parse.py`
se na konci volá centralizovaná obsluha výjimek `Error.handle_exception(e)`). Díky polymorfismu lze s různými typy výjimek nakládat jednotně nebo je
kategorizovat podle tříd. Tato dědičnost zjednodušuje rozšiřitelnost – přidání nové chyby či nového typu uzlu do AST nevyžaduje zásah do již
fungujících částí, stačí vytvořit potomka příslušné bazové třídy.

## Generování XML výstupu

Komponenta `XMLGenerator` představuje samostatný modul starající se o převod výsledného AST do **XML formátu**. I když přímo nevyužívá vzor Visitor,
dodržuje obdobný princip oddělení logiky: obsahuje metody jako `generate_class_tag(node)`, `generate_method_tag(node)` atd., z nichž každá zná
formátování konkrétního typu uzlu. Hlavní metoda `generate_XML(ASTRoot, code)` pak prochází kořenový uzel AST (objekt `ProgramNode`) a volá příslušné
metody pro vnořené uzly (třídy, metody, bloky...). Tato struktura je obdobou návštěvního přístupu – namísto jedné třídy návštěvníka s mnoha `visit`
metodami zde `XMLGenerator` nabízí mnoho pomocných metod pro různé typy uzlů a řídí jejich volání. Výhodou je opět přehlednost: formátování každého
prvku (třídy, metody, literálu atd.) je izolováno v odpovídající metodě. Případné změny ve struktuře výstupního XML (například přidání nového
atributu) tak vyžadují změnu jen v jedné metodě. Toto rozhodnutí držet generování výstupu odděleně od zbytku analýzy je v souladu s principem jedné
odpovědnosti a usnadňuje případnou výměnu výstupního formátu (např. za jiný než XML) bez nutnosti zasahovat do parseru či sémantického kontroleru.

## Zhodnocení návrhových rozhodnutí

Navržená implementace využívající vzory *fasáda* a *návštěvník* spolu s promyšlenou **dědičností** se ukázala být velmi přínosná. **Modularita**
systému dovoluje jednotlivé části vyvíjet nezávisle – změna gramatiky jazyka SOL25 ovlivní převážně `LarkParser` a definice AST, zatímco pravidla
sémantiky jsou soustředěna v `SemanticAnalyser` a úprava výstupu v `XMLGenerator`. Díky fasádě `Facade` zůstává kód funkce `main` v `parse.py`
jednoduchý a čitelný; vysoká úroveň abstrakce usnadňuje i použití skriptu v kontextu větších projektů, protože poskytuje jasně definovaný vstup a
výstup bez nutnosti znát vnitřní strukturu analyzátoru. Návrhový vzor Visitor zase **zvýšil rozšiřitelnost** a udržovatelnost sémantických kontrol –
veškerá logika je přehledně rozdělena podle typů uzlů a případné rozšíření jazyka (např. o nové konstrukce) lze podpořit doplněním nových metod
návštěvníka. Kombinace těchto vzorů navíc vnesla do kódu jasnou **logickou strukturu**: je zřejmé, která část systému co dělá, a komponenty spolu
komunikují přes omezená rozhraní. To snižuje riziko chyb a usnadňuje testování. Celkově lze říci, že zvolená architektura výrazně napomohla k čisté
implementaci – kód je díky ní přehledný, dobře organizovaný a připravený na budoucí úpravy či rozšíření.
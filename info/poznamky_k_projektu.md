# Poznámky k projektu

Kromě této stránky se řadu informací o projektu dozvíte také v [FAQ v sekci Projekt](https://moodle.vut.cz/mod/page/view.php?id=508599#Projekt).

## Studijní materiály

Pro najítí studijních materiálů asi většina použije Google, ale pokud Vám nějaký materiál opravdu pomohl pochopit nějaké téma nebo oblast Pythonu 3 nebo PHP 7/8, tak mi prosím napište a já doplním zdejší tipy.


### Python 3

1.  [Dive Into Python 3](http://www.diveintopython3.net/) (anglicky) - téměř klasika přepsaná a rozšířená pro verzi 3 od Marka Pilgrima
2.  [Non-Programmer's Tutorial for Python 3](http://en.wikibooks.org/wiki/Non-Programmer%27s_Tutorial_for_Python_3) (anglicky)
3.  [Seriál Programujte v Pythonu profesionálně na Zdrojak.cz](http://www.zdrojak.cz/serialy/python-profesionalne/) - směsice tipů a pokročilejších vlastností jazyka Python
4.  [Style Guide for Python Code](http://www.python.org/dev/peps/pep-0008/) - poměrně detailní dokument ohledně stylu psaní zdrojového kódu v Pythonu (klíčová je sekce _[Code lay-out](http://www.python.org/dev/peps/pep-0008/#code-lay-out)_)

*   [Úvod do Python 3](https://video1.fit.vutbr.cz/index.php?categ_id=1407) přednášený v rámci ak. roku 2016/2017 v IPP externistou Petrem Zemkem (přednáška je opakována s drobnými aktualizacem každým rokem).

### PHP 7/8

1.  Oficiální dokumentace s řadou užitečných komentářů (anglicky): [http://www.php.net/manual/en/](http://www.php.net/manual/en/)
2.  Český blog popisující [novinky v PHP 8 oproti PHP 7](https://blog.nette.org/cs/php-8-0-co-je-noveho-1-4)

3.  Stránka na Wikipedii se základní informací o historii a řadou užitečných odkazů: [http://en.wikipedia.org/wiki/PHP](http://en.wikipedia.org/wiki/PHP)
4.  [Tutoriál o PHP 7 na w3schools.com](https://www.w3schools.com/php7/)
5.  [Tutoriál o PHP 7 na tutorialspoint.com](http://www.tutorialspoint.com/php7/), Krátký videotutoriál [PHP 8 Unchained - Start with the New Version](https://www.tutorialspoint.com/php-8-unchained-start-with-the-new-version/index.asp)

## Tipy a triky

*   Po každém dosaženém vývojovém milníku vašeho projektu proveďte test na serveru Merlin, kde budou vaše skripty testovány.
*   Doporučuji instalovat stejné verze nástrojů (na serveru Merlin nejsou typicky nejnovější verze) na stroji, kde budete vyvíjet. Pokud tedy nebudete vyvíjet přímo vzdáleně na Merlinovi. U druhé úlohy jsem pro vás nachystali dokonce [vývojářský kontejner](https://containers.dev/), který je k dispozici v [git repozitáři IPP](https://git.fit.vutbr.cz/IPP/ipp-core). Pokud bude kontejner studenty využíván, tj. bude pozitivní zpětná vazba či konstruktivní kritika, tak pro příště nachystáme podobný i pro první úlohu.

*   Při kombinování vývoje na Windows a Linuxu si dejte pozor, že nástroj WinSCP implicitně mění konce řádků při přesunu textových souborů mezi těmito platformami.
*   Někdy není vhodné používat kopírování ukázek kódu z PDF verze zadání přes schránku, protože PDF interně některé speciální znaky (například apostrofy) sází jinak, než jaký ASCII znak je v zadání explicitně vyžadován. V těchto případech je v zadání explicitně pro daný znak uveden ASCII kód, který je pro Vás směrodatný.

### 1\. úloha (parse.py v Python 3)

*   Pro analýzu jazyka SOL lze (a je vhodné) využít vhodný **generátor syntaktických analyzátorů** pro Python 3. Můžete použít jednu z knihoven uvedených na [stránce s povolenými knihovnami](https://moodle.vut.cz/mod/page/view.php?id=508608). Druhou možností je použít externí generátor syntaktického analyzátoru, tj. nástroj, který na základě gramatiky přímo vygeneruje samostatný pythonový kód. V tomto případě ale nejprve svou volbu konzultujte na fóru.
*   Využijte vhodné vývojové prostředí, které nabízí debugger! Například:
    *   [Visual Studio Code](https://code.visualstudio.com/) s [rozšířením](https://marketplace.visualstudio.com/items?itemName=ms-python.python) pro Python,
    *   [PyCharm](https://www.jetbrains.com/pycharm/) (studenti mohou získat všechny nástroje od JetBrains zdarma),

    *   [Eclipse](https://www.eclipse.org/) + [PyDev](https://pydev.org/),

    *   [IDLE](https://docs.python.org/3/library/idle.html) (součást standardní distribuce Pythonu), 
    *   a další (např. vi/vim/gvim s vhodnými rozšířeními, geany).

### 2\. úloha (interpret v PHP)

*   Odkazy na množství jednoduchých editorů i komplexních IDE s možností ladění pro PHP najdete například [na přehledné stránce na Wikipedii](http://en.wikipedia.org/wiki/List_of_PHP_editors).
*   [PHP 5.2.4 a vyšší](https://www.php.net/manual/en/errorfunc.configuration.php#ini.display-errors) implicitně vypisuje varování a chybové hlášky na standardní výstup, čímž může poškodit například validitu výstupního XML vypisovaného na stdout. Především při ladění je vhodné nastavit si [chybové výpisy na stderr](https://stackoverflow.com/questions/17805934/redirect-php-notices-and-warnings-from-stdout-to-stderr) pomocí `ini_set('display_errors', 'stderr');` (viz [manuál PHP](https://www.php.net/manual/en/function.ini-set.php)). Z tohoto důvodu je rámec ipp-core pro 2. úlohu v PHP nachystán, aby vypisoval chybové výpisy na standardní chybový výstup.

## Objektově-orientovaný návrh

Od zadání projektu 2022/2023 (a částečně již 2021/2022) je kladen větší důraz na objektově orientovaný návrh programů. Hlavním účelem je ošahání si základů objektově orientovaného programování v PHP 8 a dobrovolně i v Python 3 jako jsou třídy, instance, metody, dědičnost, rozhraní, polymorfismus a ideálně i využití návrhových vzorů. Tuto sekci budeme postupně doplňovat i na základě zkušeností z hodnocení vašich úloh.

Při samotném návrhu se doporučuje několik základních pravidel/přístupů:

*   Jelikož v Python 3 jsou všechny metody veřejné, tak se doporučuje používat konvenci, kdy **metody** **začínající podtržítkem** jsou programátory chápány jako **neveřejné** a dvěma podtržítky jako skryté (přesněji [viz PEP 8](https://peps.python.org/pep-0008/#designing-for-inheritance)).

*   Silně zvažte uvádění [anotací u metod a funkcí](https://docs.python.org/3.10/library/typing.html), i když nemusí být použity pro typovou kontrolu, ale mají jen dokumentační charakter.


*   **Single Responsibility Principle** neboli princip jedné zodpovědnosti, který ve zkratce říká, že každá metoda by měla mít pouze jednu zodpovědnost (tj. dělat jednu věc), která je většinou přesně popsaná názvem metody. Samozřejmě není žádoucí jít do extrému, kdy každá metoda bude obsahovat jeden příkaz, protože pak zase získáme tzv. spaghetti code, kdy je kód též velmi špatně čitelný, protože se v něm nedá přes množství volání metod zorientovat. Nalezení správné míry je věcí zkušeností a zdravého úsudku. Stejně tak pozor na druhý extrém, kdy budete mít všeobjímající jedinou metodu, což je ještě horší než špagetový kód.
*   V 2. úloze tj. **v PHP 8** je **používání typových anotací** (angl. _typehints_) dle kontrol nástroje [PHPStan do úrovně 6](https://phpstan.org/user-guide/rule-levels) povinné (resp. nesplnění je bodově mírně postihováno).

### Časté chyby v 2. úloze ohledně štábní kultury a objektově orientovaného návrhu

*   Není dobrý nápad jít svou implementací proti zvyklostem použitého programovacího jazyka a snažit se do něj naroubovat vlastní styl zápisu kódu. Stejně tak není dobrý nápad ignorovat zavedenou funkcionalitu dodaného rámce (např. zpracování chyb pomocí výjimek) a snažit se stejné věci znovu vyřešit po svém. Výsledkem je pak často kód, který nesplňuje standard PSR-4 a nefunguje u něj připravené automatické načítání tříd přes Composer. Toto se snažili studenti dále opravit nešikovným používáním "include" a "require", což jen vytvořilo další problémy při statické analýze kódu.
*   Častým problémem je neznalost základních vlastností OOP, které poté studenti v projektu vůbec nevyužívají. Navržené objekty jsou pak často degradovány pouze na oddělené jmenné prostory. Často se v nich nachází statické třídní atributy; což je to stejné jako používání globálních proměnných. Nevyužívá se polymorfismus.
*   Dobrým zvykem je předávat potřebné závislosti do objektu pomocí konstruktoru (více viz např. dependency injection). O předávání závislostí se mohou centralizovaně starat továrny objektů a tato činnost nemusí prorůstat celým kódem. Častou chybou studentů je, že závislosti předávají až při volání konkrétní metody, která dané závislosti využívá. Pokud poté metodu přetěžují, tak musí u každé její nové definice znovu opakovat seznam všech závislostí. Pokud by se navíc závislosti změnily, tak pak musí všechny definice také jednotlivě upravit. V takovýchto případech je mnohem vhodnější vyřešit předávání závislostí v konstruktoru rodičovské třídy, kterou budou následně jednotlivé definice rozšiřovat pouze o nezbytný nový kód.

### Pár poznámek k návrhovým vzorům v rámci projektu

Návrhový vzor je třeba nejprve do hloubky pochopit, abyste jej mohli správně aplikovat ([přednáška o NV z 2021/2022](https://video1.fit.vutbr.cz/av/records.php?id=62293&categ_id=1887), v Souborech k přednáškám najdete snímky k přednášce o NV). V komentářích a dokumentaci je pak velmi vhodné ukázat mapování mezi jménami tříd a metod z výkladu NV a mezi implementačními jménami tříd a metod, čímž se často ukáží i specifika vaší implementace NV, které je vhodné zdůvodnit.

*   **Jedináček** \- tento návrhový vzor je možné použít pro zajištění unikátního přístupového místa, což je potřeba v paralelních či vícevláknových aplikacích, což se projektu do IPP netýká. Pro příliš časté nezdůvodněné nadužívání tohoto vzoru je někdy dokonce označován jako _antipattern_.  Navíc v dynamických jazycích PHP 8 a Python 3 je téměř nemožné implementovat skutečného jedináčka, ale pouze skoro, kdy počítáte s tím, že programátor se nebude vědomě snažit obcházet požadavek jedinečnosti jeho instance v celém programu. **Bez vskutku velmi dobrého důvodu návrhový vzor Jedináček v projektu do IPP nepoužívejte.**
*   **Návštěvník** \- návrhový vzor často spojený s interpretací či analýzou stromové struktury, což se může hodit i při interpretaci tříadresného kódu, ačkoli ten má zde velmi jednoduchou strukturu (strom je (téměř) degradován na seznam).
*   **Tovární metoda** - při potřebě pozdržet instanciaci třídy, či rozhodnutí, kterou třídu instanciovat, se hodí tento návrahový vzor.

*   **Interpret** - ... 
*   **Fasáda** - ...


Pokud se návrhový vzor nehodí, či prostě přesně nepasuje na vytvořený návrh, tak se jej nesnažte za každou cenu naroubovat. Výběr použitých návrhových vzorů v dokumentace povinně a srozumitelně zdůvodněte a uveďte, které třídy odpovídají, kterým obecným třídám návrhového vzoru (vhodné využít terminologii z přednášek nebo klasických knih o návrhových vzorech).

## Časté chyby

*   Pozor na rozdíl mezi relativní cestou vůči zpracovávanému PHP skriptu (_rel/to/script/path_) a relativní cestou vůči aktuálnímu adresáři (_./rel/to/actual/path_). V případě, že bude skript spuštěn z jiného adresáře, tak se liší a potom bude rozdílně fungovat např. funkce _require\_once()_. **Nepředpokládejte, že bude váš skript při spuštění obsažen v aktuálním adresáři!** Navíc **rámec ipp-core využívá autoloader**, takže funkce require\_once() nebude tak často využívaná.
*   Pozor na **rozdíl příkazu _return_ a _exit_** a především to, že _return_ neovlivňuje návratovou hodnotu spuštěného skriptu (pouze případnou návratovou hodnotu spuštěné funkce v rámci spuštěného skriptu) na rozdíl od _exit_, takže pro vracení správné návratové hodnoty skriptu používejte _exit_! V Python je kýžená funkce ve jmenném prostoru _sys_, tj. _sys.exit_().


### Znaková sada Unicode a její reprezentace UTF-8

*   [Unicode, Inc. Unicode Consortium. (c) 1991-2013](http://www.unicode.org/) - oficiální stránky.
*   [UTF-8 and Unicode Standards. 12. 12. 2012](http://www.utf-8.com/) - rozcestník informací a standardů.
*   Textový soubor v UTF-8, který neobsahuje žádný znak s kódem větším jak 127, je shodný se souborem v kódování ANSI (tj. starší základní znaková sada bez speciálních znaků jako diakritika, matematické symboly apod.).
*   Ve skutečnosti všechno UTF-8 kódování v projektu IPP by mělo být přesněji označováno jako UTF-8-NOBOM nebo UTF-8N kódování, protože neuvažujeme speciální hlavičku o dvou bajtech na začátku každého souboru (tzv. ''byte order mark'' zkracovaný jako ''BOM'').

### XML a jeho porovnávání

Nejprve několik upřesnění k formátu XML, jak s ním bude pracováno v projektu do IPP.

*   [Extensible Markup Language (XML) 1.0. W3C. World Wide Web Consortium. 5. vydání. 26. 11. 2008](http://www.w3.org/TR/xml/) - standard XML 1.0. Pokud se setkáváte s formátem XML poprvé, tak pro úvodní seznámení před tím, než se začtete do standardu, doporučujeme například [tutoriály o XML na w3schools.com](http://www.w3schools.com/xml/default.asp).
*   XML bude v kódování UTF-8 s podporou všech znaků.
*   Při analýze XML není třeba podporovat jmenné prostory v XML, ale musíte být schopni je ignorovat, pokud se ve vstupním XML objeví.
*   V XML je třeba bystře rozlišovat pojmy značka (anglicky ''tag'') a atribut (anglicky ''attribute''). U značek na stejné úrovni, které jsou přímým potomkem jediné rodičovské značky nezávisí na pořadí.
*   Pokud XML element (např. <code><null></null></code>) neobsahuje text, lze jej zapisovat ve zkráceném tvaru <code><null/></code>.

Již v obecném zadání je upřesněno, že pro porovnávání bude využit freewarový nástroj příkazové řádky [JExamXML](http://www.a7soft.com/downloads/jexamxml.zip) od firmy [A7Soft](http://www.a7soft.com/jexamxml.html).

*   Při práci s tímto nástrojem je třeba jako parametr explicitně uvést soubor ''options'' (jinak se bere jiné implicitní vnitřní nastavení), který bude zveřejněn u zadání projektu, kde se XML výstup očekává od skriptu parse.py.
*   JExamXML si poradí s různým pořadím XML značek (dle definice v normě formátu XML totiž nezáleží na jejich pořadí, pokud mají tentýž rodičovský uzel). Proto je třeba u elementů ''instruction'' uvádět celočíselné pořadí instrukce (povinný atribut ''order'') v rámci vstupního zdrojového kódu.
*   JExamXML by si měl poradit také s různým odřádkováním v porovnávaném XML (LF versus CR LF).
*   Konverze (či vynechání konverze) apostrofů a uvozovek v textových elementech  XML a hodnotách atributů neovlivňuje výsledek porovnání nástrojem JExamXML. Tj. nezáleží, zda je v textovém elementu ' nebo &amp;apos;. Analogicky je to s diakritikou, kdy je jedno zda je v textovém elementu ž nebo &#382;.
*   Kopie nástroje JExemXML je k dispozici i na serveru Merlin v adresáři ''/pub/courses/ipp/jexamxml'', kde lze nalézt i soubor 'options'' pro správné vnitřní nastavení nástroje. Spuštení lze pak provést příkazem na serveru Merlin následovně:

 java -jar /pub/courses/ipp/jexamxml/jexamxml.jar vas\_vystup.xml referencni.xml delta.xml /pub/courses/ipp/jexamxml/options


## Dokumentace

V této kapitolce zmíním časté chyby v dokumentaci z minulých let. Někdy se za danou chybu ani body nesrážely, ale přesto byste se měli těmto chybám či nepřesnostem vyvarovat.


Nejprve pár slov ke **zdrojovým textům a komentářům** v nich:

*   Nekombinujte mezery a tabulátory k odsazování kódu. Pokud to uděláte a někdo má nastavenou šířku tabulátoru jinak než vy, tak se struktura kódu rozsype.
*   Mnohdy byl nedostatečný popis funkcí. Minimálně by mělo být z popisu funkce zřejmé (1) co dělá, (2) jaké má parametry a (3) co vrací. Mezi doplňující informace patří např. výjimky, předpoklady pro volání funkce a práce se vstupem/výstupem.
*   Dejte si pozor na štábní kulturu v kódu (mnohdy byl kód značně nepřehledný a strukturování kódu bylo odbyté).
*   Velká část studentů nejeví snahu o vhodnou dekompozici svého skriptu na funkce nebo dokonce třídy a instance.2. úloha se na tento neduh zaměřuje.


Nyní k samotnému **textu dokumentace** v PDF:

*   Během čtení vždy narazíme na hodně překlepů, což působí dojmem, že dokumentace byla psána narychlo. Doporučujeme si před odevzdáním nechat text zkontrolovat přes některý nástroj na kontrolu pravopisu/překlepů (spellchecker).
*   Mnohdy v dokumentaci chyběl popis implementace stěžejní části (ta se podle popisovaného skriptu liší). Např. pro parse.py nás zajímá metoda použitá pro analýzu zdrojového kódu; u interpret.php nás zajímají struktury pro modelování paměti a pro podporu instrukcí řízení toku programu.
*   Někdy byl popis implementovaných funkcí nedostatečný, vágní či dokonce rozporuplný.
*   Studenti by neměli zapomenout popsat použité formy vnitřní reprezentace. Tedy které informace a jakým způsobem jsou během práce skriptu uchovávány (případně i proč, pokud to není zcela triviální důvod).
*   Problematická úprava dokumentace - neupravené zarovnání textu (doporučujeme zarovnání do bloku).
*   Ze stylistického hlediska není u technické dokumentace, kde je ze zadání jasné, že jste vše prováděli sami a nemá smysl to zdůrazňovat, vhodné používat 1. osobu jednotného čísla (tj. "já jsem implementoval", "zabýval jsem se"), ale vhodnější je používat trpný rod.
*   Ve většině dokumentací byly typografické chyby a neuvážené až zbytečné užívání anglických (slangových) termínů a hovorových výrazů.

*   parser => analyzátor
*   parsing => (syntaktická) analýza
*   parsuje => analyzuje, zpracovává
*   tag => značka

*   I přes explicitní zákaz v zadání se objevují zkopírované části zadání přímo v dokumentaci.
*   Častý výskyt pravopisných chyb, které nelze hledat automaticky (např. interpunkce v souvětích, shodu přísudku s podmětem; často dělá problém např. slovo standardní).
*   Dle typografických pravidel by se neslabičné předložky neměly objevovat osamocené na konci řádků, takže se mezi takovou předložku a následující slovo vkládá tzv. tvrdá mezera (v LaTeXu pomocí ~, ve Microsoft Word pomocí Ctrl+Shift+mezerník). V Markdown to bohužel nelze ošetřit, tak se tím v případě použití Markdown netrapte.

*   Občas nebyl dodržen minimální a někdy ani maximální rozsah dokumentace.
*   V anglických dokumentacích často chybí členy nebo jsou použity nevhodně. Dále aplikujete česká pravidla interpunkce, což je špatně. Jednotné číslo slova automat je anglicky ''automaton'' (mn. č. je ''automata'').

## Částé chyby v projektech dle hodnocení cvičících

### 2\. úloha (interpret.php)

V bodech časté prohřešky studentů:

*   Asi nejčastější chybou bylo opomnění požadavku na popis návrhu pomocí UML diagramu tříd (viz zadání).

*   Používání nepřesné nebo nesprávné terminologie (např. funkce místo metoda (nechť vás nemate nevhodné klíčové slovo function používané v syntaxi PHP), třída místo instance, anglické "list" místo českého slova "seznam"/slovenského "zoznam").
*   Ak používate Markdown, aspoň sa na vygenerovanú dokumentáciu pozrite.
*   Obecne je zlý nápad pri vypisovaní chybových hlášok ukončovať program (prípadne priamo v if/else). Používajte radšej výnimky a ukončenie programu vykonávajte v konštrukcii try/catch. Ideálne na jednom mieste (napríklad vstupný bod programu). **Nově vás 2. úloha k využívání výjimek vybízí!**

*   Diagramy často neměly označené vztahy mezi třídami. Je to podstatná část pro pochopení Vašeho návrhu.
*   ...

**_Naposledy změněno: pátek, 14. února 2025, 14.40_**
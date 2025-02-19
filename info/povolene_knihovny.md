# Povolené knihovny

Tato stránka doplňuje informace ze zadání (viz sekce Popis programové části řešení) ohledně možností a zákazů použití standardních a dalších knihoven daného jazyka pro implementaci úloh projektu IPP.


## Knihovny a moduly s explicitním schválením nebo zákazem

Seznam bývá průběžně aktualizován Seznam je rozdělen na povolené knihovny dostupné na serveru Merlin a povolené ale na serveru Merlin nedostupné knihovny. V případě doplnění zakázané knihovny budeme rozsílat i e-mailové upozornění.

### Python 3.11

Python ve verzi 3.11 je dostupný na serveru Merlin pouze přes příkaz `python3.11`. V případě vývoje mimo server Merlin silně doporučujeme vyvíjet právě na této verzi Python kvůli případným nekompatibilitám jiných verzí (pro správu více verzí Pythonu na jednom systému je možné využít např. nástroj [pyenv](https://github.com/pyenv/pyenv)). Pozor na to, že pod příkazem `python` a `python3` je na serveru Merlin starší verze 3.8.

#### Standardní knihovna

Pokud zde nejsou explicitně zakázány, můžete použít v zásadě kterékoliv moduly ze [standardní instalace Python 3.11](https://docs.python.org/release/3.11.2/library/). Jmenovitě se mohou hodit např.:

*   [argparse](https://docs.python.org/release/3.11.2/library/argparse.html) nebo [getopt](https://docs.python.org/release/3.11.2/library/getopt.html)
*   [codecs](https://docs.python.org/release/3.11.2/library/codecs.html)
*   [re](https://docs.python.org/release/3.11.2/library/re.html)
*   [xml.dom.minidom](https://docs.python.org/release/3.11.2/library/xml.dom.minidom.html)
*   [xml.etree.ElementTree](https://docs.python.org/release/3.11.2/library/xml.etree.elementtree.html)
*   [xml.parsers.expat](https://docs.python.org/release/3.11.2/library/pyexpat.html)
*   [xml.sax.handler](https://docs.python.org/release/3.11.2/library/xml.sax.handler.html)

#### Další povolené knihovny

Mimo standardní instalaci jsou **schváleny následující knihovny**:

*   lark 1.2.2: [https://pypi.org/project/lark/](https://pypi.org/project/lark/ "https://pypi.org/project/lark/")
*   parsy 2.1: [https://pypi.org/project/parsy/](https://pypi.org/project/parsy/ "https://pypi.org/project/parsy/")
*   parglare 0.18.0: [https://pypi.org/project/parglare/](https://pypi.org/project/parglare/ "https://pypi.org/project/parglare/")
*   pyparsing 3.2.1: [https://pypi.org/project/pyparsing/](https://pypi.org/project/pyparsing/)

*   PLY\*: [https://github.com/dabeaz/ply](https://github.com/dabeaz/ply)


Tyto knihovny **nejsou dostupné** v běžné systémové instalaci na serveru Merlin. Pro jejich využití (při vývoji i testování na Merlinovi) si vytvořte vlastní _virtuální prostředí_ pro Python, ve kterém si nainstalujte zvolenou knihovnu v uvedené verzi:

```bash
python3.11 -m venv myvenv  # Vytvoří virtuální prostředí (venv) v adresáři myenv (chvíli to trvá)

source myenv/bin/activate  # Aktivuje venv = upraví prostředí aktuálního shellu tak, že se místo systémové instalace Pythonu "sahá" jen do virtuální instalace "myenv"

pip3 install "lark==1.2.2"  # parsy==2.1, ...  # Nainstaluje knihovnu v konkrétní verzi

# v aktivovaném prostředí je možné nyní běžně spustit Python (pomocí 'python3.11' nebo i 'python'), který už bude využívat nainstalované knihovny
```

Místo instalace konkrétní knihovny můžete použít soubor **requirements.txt**, který najdete v _[Souborech k projektu](https://moodle.vut.cz/mod/folder/view.php?id=508604)_. Takto nainstalujete najednou všechny povolené knihovny a vaše prostředí tak bude shodné s tím, ve kterém budou projekty námi testovány.

```bash
# po aktivaci virtuálního prostředí (příkaz 'source [...]' výše) spusťte:

pip3 install -r requirements.txt
```

Virtuální prostředí ani seznam použitých knihoven **neodevzdávejte**. Vaše projekty budou testovány v námi vytvořeném prostředí, ve kterém budou všechny knihovny (mimo PLY) **už nainstalovány** (podle dodaného souboru requirements.txt).

Žádné jiné knihovny mimo standardní knihovnu a výše uvedené naopak nainstalovány nebudou (a pokud je bez schválení zahrnete do odevzdaného archivu, bude pravděpodobně hodnocen nula body). Pokud chcete využít jinou knihovnu, je nutné to probrat s [cvičícím](mailto:krivka@fit.vut.cz?subject=IPP:%20Gener%C3%A1tory%20k%C3%B3du) pomocí e-mailu nebo na fóru.

\*Výjimkou z výše uvedeného je knihovna PLY, která již není v PyPI aktualizována. Pro její využití následujte instrukce uvedené v jejím repozitáři na GitHubu (její kód pak **odevzdejte** spolu s tím vaším).

### PHP 8.4

Nová verze PHP dostupná na serveru Merlin od roku 2023 je přístupná pouze přes příkaz `php8.4`. V případě vývoje mimo server Merlin silně doporučujeme vyvíjet právě na této verzi PHP kvůli případným nekompatibilitám jiných verzí. Pozor na to, že pod příkazem `php` je na serveru Merlin PHP staré verze a navíc nakonfigurováno tak, že nemůže přistupovat k souborovému systému, a tudíž načítat ze souboru či zapisovat do souboru.

#### Povolené a dostupné na serveru Merlin

*   standardní knihovna obsahující funkce (či jejich objektové varianty) jako
*   [getopt](http://cz2.php.net/manual/en/function.getopt.php) (analýza dodatečných parametrů např. požadovaných rozšířením)

*   [DOM](http://php.net/manual/en/book.dom.php) (Document Object Model, který získáte od rámce _ipp-core_)
*   [Multibyte String](http://www.php.net/manual/en/book.mbstring.php) (pro práci s UTF-8; [instalační poznámky](http://php.net/manual/en/mbstring.installation.php))

#### Povolené, ale nedostupné na serveru Merlin (chybí ve složce vendor rámce ipp-core)

*   Aktuálně nejsou žádné další knihovny/moduly vložené pro 2. úlohu vendor pro využití

#### Zakázané knihovny

*   Zatím nejsou evidovány žádné požadavky na nevhodné/zakázané knihovny.

#### Zakázané funkce

Z bezpečnostních důvodů jsou při hodnocení vaší 2. úlohy v PHP 8.4 **ZAKÁZÁNY** tyto funkce:

`exec`, `passthru`, `proc_open`, `proc_get_status`, `proc_nice`, `proc_close`, `proc_terminate`, `shell_exec`, `system`, `pcntl_exec`, `popen,checkdnsrr`, `closelog`, `define_syslog_variables`, `dns_check_record`, `dns_get_mx`, `dns_get_record`, `fsockopen`, `gethostbyaddr`, `gethostbyname`, `gethostbynamel`, `gethostname`, `getmxrr`, `getprotobyname`, `getprotobynumber`, `getservbyname`, `getservbyport`, `header_register_callback`, `header_remove`, `header`, `headers_list`, `headers_sent`, `http_response_code`, `inet_ntop`, `inet_pton`, `ip2long`, `long2ip`, `openlog`, `pfsockopen`, `setcookie`, `setrawcookie`, `socket_create`, `socket_connect`, `socket_get_status`, `socket_set_blocking`, `socket_set_timeout`, `syslog`, `mail`, `curl_exec`, `curl_multi_exec`, `parse_ini_file`, `show_source`

Případně nutnost jejich použití konzultujte se [cvičícím.
](mailto:krivka@fit.vut.cz?subject=IPP_zakazane_knihovny)



**_Naposledy změněno: neděle, 16. února 2025, 16.54_**
################################################################################
#                                                                              #
# Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   #
#                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               #
#                                                                              #
# Soubor:           Makefile                                                   #
# Autor:            Jan Kalina   <xkalinj00>                                   #
#                                                                              #
# Datum:            20.02.2025                                                 #
# Poslední změna:   20.02.2025                                                 #
#                                                                              #
# Popis: Makefile obsahuje cíle sloužící ke spuštění Python skriptu 'parse.py' #
#        pro zvolený zdrojový soubor v jazyce SOL25. Dále obsahuje cíle určené #
#        k údržbě čistoty repozitáře (mazání Python složek apod.) a přípravy   #
#        projektu k odevzdání.                                                 #
#                                                                              #
################################################################################

################################################################################
#                                                                              #
#                  ZÁKLADNÍ NASTAVENÍ A DEFINICE PRO MAKEFILE                  #
#                                                                              #
################################################################################

###                                     ###
#  Základní konfigurace souboru Makefile  #
###                                     ###

# Název projektu
EXECUTABLE = parse

# Názvy souborů
EXECUTABLE_FILE = $(EXECUTABLE).py
TEST_FILE = test.py

# Název ZIP archivu pro odevzdání projektu
PACK_NAME = xkalinj00

# ANSI sekvence pro barvy
COLOR_RESET = \033[0m
COLOR_RED = \033[0;31m
COLOR_GREEN = \033[0;32m
COLOR_BLUE = \033[0;36m
COLOR_YELLOW = \033[0;33m
COLOR_MAGENTA = \033[0;35m


###                                       ###
#  Přepínače pro spouštění příkazu $(MAKE)  #
###                                       ###

# Spuštění 'make' v tichém režímu (bez výpisu událostí)
$(VERBOSE)SILENTOPT = -s

# Definice konstanty pro zakázání vybraných cílů (kvůli odevzdání)
#DISABLE_TARGETS ?= true


###                                                         ###
#  Deklarace cest k adresářům určeným pro kompilaci projektu  #
###                                                         ###

# Cesta k adresáři se zdrojovými soubory překladače
SRC_DIR = .

# Cesta k adresáři s testy
TEST_DIR = test
MODULE_DIR = MyPyModules

# Adresář s připraveným projektem pro zabalení
PACK_DIR = pack
ARCHIVE_DIR = $(PACK_DIR)/$(PACK_NAME)


################################################################################
#                                                                              #
#                          ZÁKLADNÍ PŘÍKAZY MAKEFILE                           #
#                                                                              #
################################################################################

# Příkaz '.PHONY' určuje, že následující příkazy nejsou nikdy brány jako soubory
.PHONY: all help run test clean pack pack-prepare venv-init venv-activate \
        venv-deactivate venv-delete install-help-dep install-pack-dep

### MC # all: # Provede sestavení celého překladače určeného k nasazení
all: run

# Definice zkratek pro kategorie příkazů
CATEGORIES := MC PY DEV O

### MC # help: # Vypíše nápovědu k použití Makefile
help:
ifndef DISABLE_TARGETS
	@$(MAKE) $(SILENTOPT) install-help-dep
endif
	@{ \
	for CATEGORY in $(CATEGORIES); do \
		case $$CATEGORY in \
		"MC") FULL_CAT="Main Commands";; \
		"PY") FULL_CAT="Python 3.11 Virtual Environment";; \
		"DEV") FULL_CAT="Install Dependencies";; \
		"O") FULL_CAT="Others";; \
		esac; \
		echo "$(COLOR_YELLOW)$$FULL_CAT:$(COLOR_RESET)"; \
		grep -E "^### $$CATEGORY # [a-zA-Z0-9_\-]+:.*?# .*$$" $(MAKEFILE_LIST) | \
		sort -f | \
		awk 'BEGIN {FS = ":.*?# "}; \
		{ \
			gsub(/^### [A-Z]+ # /, "", $$1); \
			split($$2, lines, "\\\\n"); \
			printf "$(COLOR_BLUE)%-30s$(COLOR_RESET) %s\n", $$1, lines[1]; \
			for (i = 2; i <= length(lines); i++) { \
				printf "$(COLOR_BLUE)%-30s$(COLOR_RESET) %s\n", "", lines[i]; \
			} \
		}'; \
		echo ""; \
	done; \
	} | less -R

### MC # run: # Příkaz 'clean' spustí skript 'parse.py'
run:
	python3.11 parse.py

### MC # clean: # Příkaz 'clean' odstraní adresář './build' s objektovými soubory
clean:
	rm -rf $(SRC_DIR)/__pycache__
	rm -rf $(SRC_DIR)/.pytest_cache
	rm -rf $(MODULE_DIR)/__pycache__
	rm -rf $(TEST_DIR)/__pycache__
	rm -rf $(PACK_DIR)

### MC # test: # Sestaví knihovny GoogleTest a GoogleMock a spustí test překladače
ifndef DISABLE_TARGETS
test:
	pytest $(TEST_DIR)/$(TEST_FILE)
else
test:
	@echo "$(COLOR_RED)Cíl 'test' je ve verzi projektu pro odevzdání zakázán.$(COLOR_RESET)"
endif

### MC # pack: # Vytvoří ZIP archiv se soubory určenými k odevzdání
ifndef DISABLE_TARGETS
pack:
	@$(MAKE) $(SILENTOPT) install-pack-dep
	@$(MAKE) $(SILENTOPT) clean
	mkdir -p $(PACK_DIR)
	$(MAKE) $(SILENTOPT) pack-prepare
	@echo ""
	cd $(ARCHIVE_DIR) && zip -qr ../$(PACK_NAME) ./
	@{ \
		cd "$(PACK_DIR)" && \
			mkdir is_it_ok && \
			cp $(PACK_NAME).zip is_it_ok/ && \
			cp ../$(TEST_DIR)/is_it_ok.sh is_it_ok/ && \
			cd ./is_it_ok && \
			./is_it_ok.sh $(PACK_NAME).zip testdir 1; \
	}
else
pack:
	@echo "$(COLOR_RED)Cíl 'pack' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif


################################################################################
#                                                                              #
#                  ZABALENÍ PROJEKTU PRO ODEVZDÁNÍ do '.ZIP'                   #
#                                                                              #
################################################################################

### O # pack-prepare: # Zkopíruje všechny potřebné soubory do adresáře '../pack/xkalinj00'
ifndef DISABLE_TARGETS
pack-prepare:
	@{ \
		missing_files=0; \
		if [ -d "$(SRC_DIR)" ]; then \
			rsync -a --include '*/' --include '*.py' --exclude '*' \
			--prune-empty-dirs $(SRC_DIR)/ $(ARCHIVE_DIR)/; \
		else \
			echo "$(COLOR_RED)Error: Adresář '$(SRC_DIR)' neexistuje.$(COLOR_RESET)"; \
		fi; \
		if [ -d "$(MODULE_DIR)" ]; then \
			rsync -a $(MODULE_DIR) $(ARCHIVE_DIR)/; \
		else \
			echo "$(COLOR_RED)Error: Adresář '$(MODULE_DIR)' neexistuje.$(COLOR_RESET)"; \
		fi; \
		if [ -d "$(TEST_DIR)" ]; then \
			rsync -a --include '*/' --include '*.py' --exclude '*' \
			--prune-empty-dirs $(TEST_DIR)/ $(ARCHIVE_DIR)/test/; \
		else \
			echo "$(COLOR_RED)Error: Adresář '$(TEST_DIR)' neexistuje.$(COLOR_RESET)"; \
		fi; \
		if [ -f "../rozsireni" ]; then \
			rsync -a ../rozsireni $(ARCHIVE_DIR)/; \
		else \
			missing_files=1; \
		fi; \
		if [ -f "../readme1.pdf" ]; then \
			rsync -a ../readme1.pdf $(ARCHIVE_DIR)/; \
		elif [ -f "../readme1.md" ]; then \
			rsync -a ../readme1.md $(ARCHIVE_DIR)/; \
		else \
			missing_files=1; \
		fi; \
		echo "$(COLOR_GREEN)\nSeznam zkopírovaných souborů:$(COLOR_RESET)"; \
		find $(PACK_DIR) -type f -printf "$(COLOR_GREEN)%p$(COLOR_RESET)\n"; \
		if [ "$$missing_files" -eq 1 ]; then \
			echo "$(COLOR_RED)\nSeznam chybějících souborů:$(COLOR_RESET)"; \
		fi; \
		if [ ! -f "$(ARCHIVE_DIR)/readme1.pdf" ] && [ ! -f "$(ARCHIVE_DIR)/readme1.md" ]; then \
			echo "$(COLOR_RED)Error: Soubor \"readme1.[pdf\|md]\" nebyl zkopírován.$(COLOR_RESET)"; \
		fi; \
		if [ ! -f "$(ARCHIVE_DIR)/rozsireni" ]; then \
			echo "$(COLOR_YELLOW)Error: Soubor \"rozsireni\" nebyl zkopírován.$(COLOR_RESET)"; \
		fi; \
	}
else
pack-prepare:
	@echo "$(COLOR_RED)Cíl 'pack-prepare' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif


################################################################################
#                                                                              #
#                  PŘÍPRAVA VIRTUÁLNÍHO PROSTŘEDÍ PYTHON 3.11                  #
#                                                                              #
################################################################################

### PY # venv-init: # Vytvoří virtuální prostředí (venv) v adresáři 'myenv'
ifndef DISABLE_TARGETS
venv-init:
	@echo "$(COLOR_MAGENTA)Vytvářím virtuální prostředí Python 3.11 pro tento projekt...$(COLOR_RESET)"
	python3.11 -m venv myenv
	@echo "$(COLOR_MAGENTA)Virtuální prostředí bylo úspěšně vytvořeno. Šťastný vývoj!$(COLOR_RESET)"
	@echo -e "$(COLOR_YELLOW)Pro dokončení nastavení prostředí použijte příkaz:\n'source myenv/bin/activate && pip3 install \"lark==1.2.2\" \"parglare==0.18.0\" \"parsy==2.1\" \"pyparsing==3.2.1\"'$(COLOR_RESET)"
else
venv-init:
	@echo "$(COLOR_RED)Cíl 'venv-init' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif

### PY # venv-activate: # Aktivuje virtuální prostředí inicializované v adresáři 'myenv'
ifndef DISABLE_TARGETS
venv-activate:
	@if [ ! -d "myenv" ]; then \
		echo "$(COLOR_RED)Adresář 'myenv' neexistuje, spouštím cíl 'venv-init'...$(COLOR_RESET)"; \
		$(MAKE) venv-init; \
	fi
	@echo "$(COLOR_YELLOW)Pro aktivaci prostředí použijte příkaz: 'source myenv/bin/activate'$(COLOR_RESET)"
else
venv-activate:
	@echo "$(COLOR_RED)Cíl 'venv-activate' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif

### PY # venv-deactivate: # Cíl 'venv-deactivate' zatím nebyl implementován.
ifndef DISABLE_TARGETS
venv-deactivate:
	@echo "$(COLOR_YELLOW)Pro deaktivaci prostředí použijte příkaz: 'deactivate'$(COLOR_RESET)"
else
venv-deactivate:
	@echo "$(COLOR_RED)Cíl 'venv-deactivate' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif

### PY # venv-delete: # Cíl 'venv-delete' zatím nebyl implementován.
ifndef DISABLE_TARGETS
venv-delete:
	rm -rf myenv
else
venv-delete:
	@echo "$(COLOR_RED)Cíl 'venv-delete' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif


################################################################################
#                                                                              #
#                      INSTALACE ZÁVISLOSTÍ CÍLŮ MAKEFILE                      #
#                                                                              #
################################################################################

### DEV # install-help-dep: # Nainstaluje závislosti potřebné pro výpis nápovědy k 'Makefile'
ifndef DISABLE_TARGETS
install-help-dep:
	@dpkg -s less >/dev/null 2>&1 || ( \
		read -p "$(COLOR_MAGENTA)Chcete nainstalovat nástroj 'less' potřebný k výpisu nápovědy? (y/n):$(COLOR_RESET) " ans; \
		if [ "$$ans" != "y" ]; then \
			echo "$(COLOR_RED)Akce byla zrušena.$(COLOR_RESET)"; \
			exit 1; \
		fi; \
		echo "$(COLOR_YELLOW)Instaluji less...$(COLOR_RESET)"; \
		sudo apt-get install less \
	)
else
install-help-dep:
	@echo "$(COLOR_RED)Cíl 'install-help-dep' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif

### DEV # install-pack-dep: # Nainstaluje závislosti potřebné pro zabalení projektu
ifndef DISABLE_TARGETS
install-pack-dep:
	@dpkg -s rsync >/dev/null 2>&1 && dpkg -s zip >/dev/null 2>&1 || ( \
		read -p "$(COLOR_MAGENTA)Chcete nainstalovat nástroje 'rsync' a 'zip' potřebné k zabalení projektu? (y/n):$(COLOR_RESET) " ans; \
		if [ "$$ans" != "y" ]; then \
			echo "$(COLOR_RED)Akce byla zrušena.$(COLOR_RESET)"; \
			exit 1; \
		fi; \
		echo "$(COLOR_YELLOW)Instaluji zip...$(COLOR_RESET)"; \
		sudo apt-get install zip; \
		echo "$(COLOR_YELLOW)Instaluji rsync...$(COLOR_RESET)"; \
		sudo apt-get install rsync \
	)
	@dpkg -s zip >/dev/null 2>&1 || ( \
		read -p "$(COLOR_MAGENTA)Chcete nainstalovat nástroj 'zip' potřebný k zabalení projektu? (y/n):$(COLOR_RESET) " ans; \
		if [ "$$ans" != "y" ]; then \
			echo "$(COLOR_RED)Akce byla zrušena.$(COLOR_RESET)"; \
			exit 1; \
		fi; \
		echo "$(COLOR_YELLOW)Instaluji zip...$(COLOR_RESET)"; \
		sudo apt-get install zip; \
	)
	@dpkg -s rsync >/dev/null 2>&1 || ( \
		read -p "$(COLOR_MAGENTA)Chcete nainstalovat nástroj 'rsync' potřebný k zabalení projektu? (y/n):$(COLOR_RESET) " ans; \
		if [ "$$ans" != "y" ]; then \
			echo "$(COLOR_RED)Akce byla zrušena.$(COLOR_RESET)"; \
			exit 1; \
		fi; \
		echo "$(COLOR_YELLOW)Instaluji rsync...$(COLOR_RESET)"; \
		sudo apt-get install rsync \
	)
else
install-pack-dep:
	@echo "$(COLOR_RED)Cíl 'install-pack-dep' je zakázán pro odevzdání projektu.$(COLOR_RESET)"
endif

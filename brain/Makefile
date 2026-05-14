SHELL := /bin/bash
BASE  := $(HOME)/Pandora/brain
VAULT := $(HOME)/Pandora/vault
REPO  := $(HOME)/Pandora
PY    := $(BASE)/venv/bin/python
PIP   := $(BASE)/venv/bin/pip

.PHONY: help install start stop restart status logs update clean

help:
	@echo ""
	@echo "  Pandora Brain"
	@echo ""
	@echo "  make install    full setup from scratch"
	@echo "  make start      start all processes"
	@echo "  make stop       stop all processes"
	@echo "  make restart    restart all processes"
	@echo "  make status     show health"
	@echo "  make logs       live logs"
	@echo "  make update     pull latest and restart"
	@echo "  make clean      remove venv"
	@echo ""

install:
	@echo "Installing Pandora..."
	@$(MAKE) _check
	@$(MAKE) _venv
	@$(MAKE) _packages
	@$(MAKE) _node
	@$(MAKE) _ollama
	@$(MAKE) _hybrid_search
	@$(MAKE) _pm2
	@$(MAKE) _hooks
	@echo ""
	@echo "Done. Open Obsidian, select $(VAULT)"
	@echo "Then: make start"
	@echo ""

_check:
	@command -v python3 >/dev/null || \
		(echo "Install Python: python.org" && exit 1)
	@command -v node >/dev/null || \
		(echo "Install Node: nodejs.org" && exit 1)
	@command -v git >/dev/null || \
		(echo "Install Git: git-scm.com" && exit 1)
	@command -v ollama >/dev/null || \
		(echo "Install Ollama: ollama.ai" && exit 1)
	@echo "All dependencies found"

_venv:
	@python3.11 -m venv $(BASE)/venv
	@echo "Virtual environment ready"

_packages:
	@$(PIP) install --upgrade pip -q
	@$(PIP) install -r $(BASE)/requirements.txt -q
	@echo "Python packages installed"

_node:
	@npm install -g pm2 && npm install -g obsidian-hybrid-search
	@echo "Node packages installed"

_ollama:
	@ollama serve >/dev/null 2>&1 & sleep 3
	@ollama pull llama3 --quiet 2>/dev/null || true
	@ollama pull mxbai-embed-large --quiet 2>/dev/null || true
	@echo "Ollama models ready"

_hybrid_search:
	@obsidian-hybrid-search init --vault $(VAULT) 2>/dev/null || true
	@echo "Hybrid search ready"

_pm2:
	@pm2 delete all 2>/dev/null || true
	@pm2 start $(BASE)/pandora.config.js
	@pm2 save
	@pm2 startup launchd -u pan --hp $(HOME) \
		2>/dev/null | grep sudo | bash || true
	@echo "pm2 configured"

_hooks:
	@if [ -d "$(REPO)/.git" ]; then \
		cp $(BASE)/scripts/post-commit \
		   $(REPO)/.git/hooks/post-commit && \
		chmod +x $(REPO)/.git/hooks/post-commit && \
		echo "Git hooks installed"; \
	else \
		echo "Skipping hooks — run after git init"; \
	fi

start:
	@ollama serve >/dev/null 2>&1 & true
	@pm2 start $(BASE)/pandora.config.js 2>/dev/null \
		|| pm2 restart all
	@pm2 status

stop:
	@pm2 stop all

restart:
	@pm2 restart all

status:
	@pm2 status

logs:
	@pm2 logs

update:
	@cd $(REPO) && git pull
	@$(PIP) install -r $(BASE)/requirements.txt -q
	@pm2 restart all
	@echo "Updated"

clean:
	@pm2 stop all 2>/dev/null || true
	@rm -rf $(BASE)/venv

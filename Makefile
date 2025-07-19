include .env
export $(shell sed 's/=.*//' .env)

SCRIPTS_DIR := ./scripts

.PHONY: set-webhook delete-webhook

set-webhook:
	@echo "🔗 Setting webhook..."
	@$(SCRIPTS_DIR)/set_webhook.sh

delete-webhook:
	@echo "❌ Deleting webhook..."
	@$(SCRIPTS_DIR)/delete_webhook.sh
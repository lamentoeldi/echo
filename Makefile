include .env
export $(shell sed 's/=.*//' .env)

SCRIPTS_DIR := ./scripts

.PHONY: set-webhook delete-webhook

# Set Telegram Bot API webhook
set-webhook:
	@echo "🔗 Setting webhook..."
	@$(SCRIPTS_DIR)/set_webhook.sh

# Delete Telegram Bot API webhook
delete-webhook:
	@echo "❌ Deleting webhook..."
	@$(SCRIPTS_DIR)/delete_webhook.sh

# Build go proto pb
proto-go:
	protoc --go_out=./services/tgdb/pkg \
				--go-grpc_out=./services/tgdb/pkg \
				--grpc-gateway_out=./services/tgdb/pkg \
				./api/proto/*.proto -I=./api/proto
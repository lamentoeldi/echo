include .env
export $(shell sed 's/=.*//' .env)

SCRIPTS_DIR := ./scripts

# Set Telegram Bot API webhook
.PHONY: set-webhook
set-webhook:
	@echo "🔗 Setting webhook..."
	@$(SCRIPTS_DIR)/set_webhook.sh

# Delete Telegram Bot API webhook
.PHONY: delete-webhook
delete-webhook:
	@echo "❌ Deleting webhook..."
	@$(SCRIPTS_DIR)/delete_webhook.sh

# Build go proto pb
.PHONY: proto-go
proto-go:
	protoc --go_out=./services/tgdb/pkg \
				--go-grpc_out=./services/tgdb/pkg \
				--grpc-gateway_out=./services/tgdb/pkg \
				./api/proto/*.proto -I=./api/proto

# Build python proto pb
.PHONY: proto-python
proto-python:
	python \
		-m grpc_tools.protoc \
  		-I./api/proto \
  		--python_out=./services/bot/src/adapters/repository/grpc \
  		--grpc_python_out=./services/bot/src/adapters/repository/grpc \
  		./api/proto/tgdb.proto

# Build go mocks
.PHONY: mock-go
mock-go:
	mockgen \
		-source=./services/tgdb/internal/ports/input.go \
		-destination=./services/tgdb/pkg/mock/mock_input.go \
		-package=mock
	mockgen \
    		-source=./services/tgdb/internal/ports/output.go \
    		-destination=./services/tgdb/pkg/mock/mock_output.go \
    		-package=mock

# Create dev container registry secret
.PHONY: registry-secret-dev
registry-secret-dev:
	kubectl create secret docker-registry $(REGISTRY_SECRET_NAME) \
      --docker-server=$(REGISTRY_ADDRESS) \
      --docker-username=$(REGISTRY_USERNAME) \
      --docker-password=$(REGISTRY_PASSWORD) \
      --docker-email=$(REGISTRY_EMAIL) \
      --dry-run=client -o yaml > k8s/dev/secret.yaml

# Roll up dev k8s cluster
.PHONY: rollup-dev
rollup-dev:
	kubectl apply -f k8s/dev/namespace.yaml
	kubectl apply -f k8s/dev/secret.yaml
	kubectl apply -R -f k8s/dev

# Roll back dev k8s cluster
.PHONY: rollback-dev
rollback-dev:
	kubectl delete -R -f k8s/dev
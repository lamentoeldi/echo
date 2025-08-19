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

# Get webhook info
.PHONY:
info-webhook:
	@echo "Fetching webhook info..."
	@$(SCRIPTS_DIR)/get_webhook_info.sh

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
	helm upgrade --install metallb metallb \
	  --repo https://metallb.github.io/metallb \
	  --namespace metallb-system \
	  --create-namespace
	sleep 15
	kubectl apply -f k8s/dev/metallb
	helm upgrade --install ingress-nginx ingress-nginx \
      --repo https://kubernetes.github.io/ingress-nginx
	kubectl apply -R -f k8s/dev

# Roll back dev k8s cluster
.PHONY: rollback-dev
rollback-dev:
	helm uninstall metallb -n metallb-system
	helm uninstall ingress-nginx
	kubectl delete -R -f k8s/dev

# Start grok
.PHONY: start-ngrok
start-ngrok:
	docker run -d --name ngrok \
	  --network=host \
      -e NGROK_AUTHTOKEN="${NGROK_AUTHTOKEN}" \
      ngrok/ngrok:latest \
      http --url="${NGROK_BASE_URL}" "${INGRESS_ENDPOINT}"

# Stop ngrok
.PHONY: stop-ngrok
stop-ngrok:
	docker stop ngrok
	docker rm ngrok

# Start cloudflared
.PHONY: start-cloudflared
start-cloudflared:
	docker run --net=host --rm -d --name cloudflared \
	  cloudflare/cloudflared:latest tunnel \
	  --url ${INGRESS_ENDPOINT}

# Stop cloudflared
.PHONY: stop-cloudflared
stop-cloudflared:
	docker stop cloudflared

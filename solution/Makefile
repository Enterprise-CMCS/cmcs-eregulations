.PHONY: help
help: ## Show this help.
	@egrep '^[a-zA-Z_\.%-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: local
local: ## Create a local environment with parts 400 and 433 loaded.
local: local.check local.start local.deploy local.data
	@echo Local environment started. Visit http://TODO FILL THIS IN

.PHONY: local.check
local.check: ## Verify local dependencies are installed.
local.check:
ifeq (,$(wildcard ${HOME}/.localstack/default.env))
	@mkdir -p ~/.localstack
	@cp default.env.template ~/.localstack/default.env
	@echo New installation detected. The default LocalStack profile has been copied to ~/.localstack/default.env.
	@echo Edit this file and replace LOCALSTACK_AUTH_TOKEN with your unique token. Do not commit this token to Git.
	@exit 1
else ifeq (,$(shell which localstack))
	@echo Failed to find LocalStack!
	@echo Be sure LocalStack is installed and \"which localstack\" returns a valid path.
	@exit 1
else ifeq (,$(shell which aws))
	@echo Failed to find the AWS CLI!
	@echo Be sure the official AWS CLI is installed and \"which aws\" returns a valid path.
	@exit 1
else ifeq (,$(shell which awslocal))
	@echo Failed to find awslocal!
	@echo Be sure awslocal is installed and \"which awslocal\" returns a valid path!
	@exit 1
else ifeq (,$(shell which serverless))
	@echo Failed to find serverless!
	@echo Be sure serverless is installed and \"which serverless\" returns a valid path.
	@exit 1
endif

.PHONY: local.start
local.start: ## Start the persistent LocalStack container.
local.start: local.check
	@localstack start -d
	@echo LocalStack started.

.PHONY: local.stop
local.stop: ## Stop the persistent LocalStack container.
local.stop: local.check
	@localstack stop
	@echo LocalStack stopped.

.PHONY: local.deploy
local.deploy: ## Deploy a local environment using LocalStack.
local.deploy: local.check
	@./localstack/populate_ssm
	@echo Stack created.

.PHONY: local.data
local.data: ## Seed the database with initial values.
local.data: local.check
	@echo Data seeded.

.PHONY: static-assets
static-assets: ## Build the static assets for eRegs.
static-assets: local.check ui/regulations/node_modules static-assets/regulations/css/main.css ui/regulations/eregs-component-lib/node_modules static-assets/regulations/js/eregs-main.iife.js ui/regulations/eregs-vite/node_modules build-spa

ui/regulations/node_modules: ui/regulations/package.json
	cd ui/regulations; \
		npm install;

ui/regulations/eregs-vite/node_modules: ui/regulations/eregs-vite/package.json
	cd ui/regulations/eregs-vite; \
		npm install;

ui/regulations/eregs-component-lib/node_modules: ui/regulations/eregs-component-lib/package.json
	cd ui/regulations/eregs-component-lib; \
		npm install;

static-assets/regulations/css/main.css: ui/regulations/css/**/*.scss
	cd ui/regulations; \
		npm run css; \
		mkdir ../../static-assets/regulations/css/admin/; \
		cp css/admin/*.css ../../static-assets/regulations/css/admin/;

static-assets/regulations/js/eregs-main.iife.js: ui/regulations/eregs-component-lib/src/main.js ui/regulations/eregs-component-lib/src/components/*.vue
	cd ui/regulations/eregs-component-lib; \
		npm run build;

.PHONY: build-spa
build-spa: ## Build vite assets
build-spa:
	cd ui/regulations/eregs-vite; \
		npm run build;



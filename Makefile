.PHONY: help
help: ## Show this help.
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

regulations-site: ## Build regulations-site assets
regulations-site: regulations-site/regulations/static/regulations/css/main.css

regulations-site/regulations/static/node_modules: regulations-site/regulations/static/package.json
	cd regulations-site/regulations/static; \
		npm install;

regulations-site/regulations/static/regulations/css/main.css: regulations-site/regulations/static/node_modules regulations-site/regulations/static/regulations/css/**/*.scss
	cd regulations-site/regulations/static; \
		npm run css;

.PHONY: watch
watch: ## Watch regulations-site static assets and rebuild when they're changed
	cd regulations-site/regulations/static; \
		npm run watch-css;

.PHONY: sync
sync: ## Sync the submodules regualtions-site, core, parser
	git submodule update --init

local: ## Start a local environment with parts 400 and 433 loaded.
local: local.docker local.data.400 local.data.433
	@echo Local environment started. Visit http://localhost:8000

regulations-parser/Dockerfile.local: config/regulations-parser/Dockerfile
	cp config/regulations-parser/Dockerfile regulations-parser/Dockerfile.local

local.docker: ## Start a local environment
local.docker: regulations-parser/Dockerfile.local
	docker-compose up -d; \
		sleep 5; \
		make local.regulations-core; \
		docker-compose exec regulations-parser pip install -r requirements.txt;

local.regulations-core: ## Run migrations and restart the regulations-core
	docker-compose exec regulations-core python manage.py migrate; \
		docker-compose restart regulations-core;

local.parser: ## Update the regulations-parser with the latest code
	docker-compose exec regulations-parser pip install -e .;

local.data.%: ## Load a Part of Title 42. e.g. make load.data.435 will load Part 435
local.data.%: local.parser
	docker-compose exec regulations-parser eregs pipeline 42 $(firstword $(subst ., ,$*)) http://regulations-core:8080

local.stop: ## Stop the local environment, freeing up resources and ports without destroying data.
	docker-compose stop

local.start: ## Start the local environment if stopped using `make local.stop`
	docker-compose start

local.clean: ## Remove the local environment entirely.
	docker-compose down
	docker volume rm cmcs-eregulations_eregs-cache

test: ## run the cypress e2e suite
	docker-compose up e2e 

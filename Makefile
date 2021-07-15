.PHONY: help
help: ## Show this help.
	@egrep '^[a-zA-Z_\.%-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

regulations: ## Build regulations assets
regulations: regulations/static/regulations/css/main.css regulations/static/regulations/js/main.build.js

regulations/static/node_modules: regulations/static/package.json
	cd regulations/static; \
		npm install;

regulations/static/regulations/css/main.css: regulations/static/node_modules regulations/static/regulations/css/**/*.scss
	cd regulations/static; \
		npm run css;

regulations/static/regulations/js/main.build.js: regulations/static/regulations/js/main.js regulations/static/components/*.js
	cd regulations/static; \
		npm run js;

.PHONY: watch
watch: ## Watch regulations static assets and rebuild when they're changed
	cd regulations/static; \
		(trap 'kill 0' SIGINT; npm run watch-js & npm run watch-css);

.PHONY: storybook
storybook: ## Run storybook for regulations
storybook: regulations/static/node_modules
	cd regulations/static; \
		npm run storybook

.PHONY: lint
lint:
	flake8; \
	golint -set_exit_status tools/...;

local: ## Start a local environment with parts 400 and 433 loaded.
local: local.docker data.local
	@echo Local environment started. Visit http://localhost:8000

local.docker: ## Start a local environment
local.docker:
	docker-compose up -d; \
		sleep 5; \
		make local.regulations-core;

local.regulations-core: ## Run migrations and restart the regulations-core
	docker-compose exec regulations python manage.py migrate; \
		docker-compose restart regulations; \
		sleep 5;

tools/ecfr-parser/build/ecfr-parser: tools/ecfr-parser/*.go tools/ecfr-parser/**/*.go
	cd tools/ecfr-parser; go build -o build/ecfr-parser .

data.prod: ## Load a Part of Title 42. e.g. make data.prod.435 will load Part 435 into prod
data.prod: CORE_URL = https://5jk91taqo5.execute-api.us-east-1.amazonaws.com/prod/v2/

data.val: ## Load a Part of Title 42. e.g. make data.val.435 will load Part 435 into val
data.val: CORE_URL = https://0pu9rqbvjd.execute-api.us-east-1.amazonaws.com/val/v2/

data.dev: ## Load a Part of Title 42. e.g. make dev.data.435 will load Part 435 into dev
data.dev: CORE_URL = https://w1tu417grc.execute-api.us-east-1.amazonaws.com/dev/v2/

data.local: ## Load a Part of Title 42. e.g. make data.local.435 will load Part 435
data.local: CORE_URL = http://localhost:8000/v2/
data.local: export EREGS_USERNAME=RpSS01rhbx
data.local: export EREGS_PASSWORD=UkOAsfkItN

data.%: tools/ecfr-parser/build/ecfr-parser
	./tools/ecfr-parser/build/ecfr-parser -title 42 -subchapter IV-C -parts 400,457,460 -eregs-url $(CORE_URL)

local.stop: ## Stop the local environment, freeing up resources and ports without destroying data.
	docker-compose stop

local.start: ## Start the local environment if stopped using `make local.stop`
	docker-compose start

local.clean: ## Remove the local environment entirely.
	docker-compose down
	docker volume rm cmcs-eregulations_eregs-data

test: ## run the cypress e2e suite
	docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up e2e

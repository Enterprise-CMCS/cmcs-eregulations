.PHONY: help
help: ## Show this help.
	@egrep '^[a-zA-Z_\.%-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

regulations-site: ## Build regulations-site assets
regulations-site: regulations-site/regulations/static/regulations/css/main.css regulations-site/regulations/static/regulations/js/main.build.js

regulations-site/regulations/static/node_modules: regulations-site/regulations/static/package.json
	cd regulations-site/regulations/static; \
		npm install;

regulations-site/regulations/static/regulations/css/main.css: regulations-site/regulations/static/node_modules regulations-site/regulations/static/regulations/css/**/*.scss
	cd regulations-site/regulations/static; \
		npm run css;

regulations-site/regulations/static/regulations/js/RelatedRule.js: regulations-site/regulations/static/components/*.vue
	cd regulations-site/regulations/static; \
		npm run vue;

regulations-site/regulations/static/regulations/js/main.build.js: regulations-site/regulations/static/regulations/js/RelatedRule.js
	cd regulations-site/regulations/static; \
		npm run js;

.PHONY: watch
watch: ## Watch regulations-site static assets and rebuild when they're changed
	cd regulations-site/regulations/static; \
		npm run watch-css;

.PHONY: storybook
storybook: ## Run storybook for regulations-site
	cd regulations-site/regulations/static; \
		npm run storybook

.PHONY: sync
sync: ## Sync the submodules regualtions-site, core, parser
	git submodule update --init

local: ## Start a local environment with parts 400 and 433 loaded.
local: local.docker data.local
	@echo Local environment started. Visit http://localhost:8000

local.docker: ## Start a local environment
local.docker:
	docker-compose up -d; \
		sleep 5; \
		make local.regulations-core;

local.regulations-core: ## Run migrations and restart the regulations-core
	docker-compose exec regulations-core python manage.py migrate; \
		docker-compose restart regulations-core; \
		sleep 5;

ecfr-parser/build/ecfr-parser: ecfr-parser/*.go ecfr-parser/**/*.go
	cd ecfr-parser; go build -o build/ecfr-parser .

data.prod: ## Load a Part of Title 42. e.g. make data.prod.435 will load Part 435 into prod
data.prod: CORE_URL = https://5jk91taqo5.execute-api.us-east-1.amazonaws.com/prod/v2/

data.val: ## Load a Part of Title 42. e.g. make data.val.435 will load Part 435 into val
data.val: CORE_URL = https://0pu9rqbvjd.execute-api.us-east-1.amazonaws.com/val/v2/

data.dev: ## Load a Part of Title 42. e.g. make dev.data.435 will load Part 435 into dev
data.dev: CORE_URL = https://w1tu417grc.execute-api.us-east-1.amazonaws.com/dev/v2/

data.local: ## Load a Part of Title 42. e.g. make data.local.435 will load Part 435
data.local: CORE_URL = http://localhost:8080/v2/
data.local: export EREGS_USERNAME=RpSS01rhbx
data.local: export EREGS_PASSWORD=UkOAsfkItN

data.%: ecfr-parser/build/ecfr-parser
	./ecfr-parser/build/ecfr-parser -title 42 -subchapter IV-C -parts 400,457,460 -eregs-url $(CORE_URL)

local.stop: ## Stop the local environment, freeing up resources and ports without destroying data.
	docker-compose stop

local.start: ## Start the local environment if stopped using `make local.stop`
	docker-compose start

local.clean: ## Remove the local environment entirely.
	docker-compose down
	docker volume rm cmcs-eregulations_eregs-data

test: ## run the cypress e2e suite
	docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up e2e

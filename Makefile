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

regulations/static/regulations/js/main.build.js: regulations/static/regulations/js/main.js regulations/static/components/*.vue
	cd regulations/static; \
		npm run js;

.PHONY: watch
watch: ## Watch regulations static assets and rebuild when they're changed
watch: regulations/static/node_modules
	cd regulations/static; \
		(trap 'kill 0' SIGINT; npm run watch-js & npm run watch-css);

.PHONY: storybook
storybook: ## Run storybook for regulations
storybook: regulations/static/node_modules
	cd regulations/static; \
		npm run storybook

.PHONY: lint
lint:
	flake8;

local: ## Start a local environment with parts 400 and 433 loaded.
local: local.docker data.local
	@echo Local environment started. Visit http://localhost:8000

local.docker: ## Start a local environment
local.docker:
	docker-compose up -d; \
		sleep 5; \
		make local.regulations;

local.regulations: ## Run migrations and restart the regulations-core
	docker-compose exec regulations python manage.py migrate; \
		docker-compose restart regulations; \
		sleep 5;

tools/ecfr-parser/build/ecfr-parser: tools/ecfr-parser/*.go tools/ecfr-parser/**/*.go
	cd tools/ecfr-parser; go build -o build/ecfr-parser .

data.prod: ## Load a Part of Title 42. e.g. make data.prod.435 will load Part 435 into prod
data.prod: CORE_URL = https://3iok6sq3ui.execute-api.us-east-1.amazonaws.com/prod/v2/
date.prod: SUPPLEMENTAL_URL = $(CORE_URL)supplemental_content

data.val: ## Load a Part of Title 42. e.g. make data.val.435 will load Part 435 into val
data.val: CORE_URL = https://qavc1ytrff.execute-api.us-east-1.amazonaws.com/val/v2/
date.val: SUPPLEMENTAL_URL = $(CORE_URL)supplemental_content

data.dev: ## Load a Part of Title 42. e.g. make dev.data.435 will load Part 435 into dev
data.dev: CORE_URL = https://hittwbzqah.execute-api.us-east-1.amazonaws.com/dev/v2/
date.dev: SUPPLEMENTAL_URL = $(CORE_URL)supplemental_content

data.experimental: ## Load a Part of Title 42. e.g. make data.experimental URL=[experimental lambda URL] into dev-experimental
data.experimental: CORE_URL = $(URL)/v2/
data.experimental: SUPPLEMENTAL_URL = $(CORE_URL)supplemental_content

data.local: ## Load a Part of Title 42. e.g. make data.local.435 will load Part 435
data.local: CORE_URL = http://localhost:8000/v2/
data.local: SUPPLEMENTAL_URL = $(CORE_URL)supplemental_content
data.local: export EREGS_USERNAME=RpSS01rhbx
data.local: export EREGS_PASSWORD=UkOAsfkItN

data.%:
	TITLE=42 \
	SUBCHAPTER=IV-C \
	PARTS=400,457,460 \
	EREGS_URL=$(CORE_URL) \
	WORKERS=3 \
	ATTEMPTS=3 \
	LOGLEVEL=trace \
	LOG_PARSE_ERRORS=false \
	EREGS_SUPPLEMENTAL_URL=$(SUPPLEMENTAL_URL) \
	SKIP_EXISTING_VERSIONS=true \
	docker-compose -f docker-compose.yml -f docker-compose.parser.yml up parser

tools/guidance_pipeline/build/guidance_pipeline: tools/guidance_pipeline/*.go
	cd tools/guidance_pipeline; go build -o build/ .

serverless/guidance/*.json: tools/guidance_pipeline/build/guidance_pipeline
	./tools/guidance_pipeline/build/guidance_pipeline -f tools/guidance_pipeline/guidances.txt -o serverless/guidance

supplemental_content: ## Load old supplemental content into a folder
supplemental_content: serverless/guidance/*.json

local.stop: ## Stop the local environment, freeing up resources and ports without destroying data.
	docker-compose stop

local.start: ## Start the local environment if stopped using `make local.stop`
	docker-compose start

local.clean: ## Remove the local environment entirely.
	docker-compose down --remove-orphans --volumes

local.createadmin: ## Create a local admin account.
	docker-compose exec regulations python manage.py createsuperuser

test: ## run the cypress e2e suite
	docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up e2e
test.local: ## run cypress tests locally without docker
	cd e2e; \
		npm install; \
		npm run cypress:run;

local.seed:
	docker-compose exec regulations python manage.py loaddata supplemental_content.category.json
	docker-compose exec regulations python manage.py loaddata supplemental_content.subcategory.json
	docker-compose exec regulations python manage.py loaddata supplemental_content.section.json
	docker-compose exec regulations python manage.py loaddata supplemental_content.supplementalcontent.json


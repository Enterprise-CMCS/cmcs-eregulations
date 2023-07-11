.PHONY: help
help: ## Show this help.
	@egrep '^[a-zA-Z_\.%-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

regulations: ## Build regulations assets
regulations: ui/regulations/node_modules static-assets/regulations/css/main.css ui/regulations/eregs-component-lib/node_modules static-assets/regulations/js/eregs-main.iife.js ui/regulations/eregs-vite/node_modules build-spa

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
		npm run css;\
		mkdir ../../static-assets/regulations/css/admin/;\
		cp css/admin/*.css ../../static-assets/regulations/css/admin/;

static-assets/regulations/js/eregs-main.iife.js: ui/regulations/eregs-component-lib/src/main.js ui/regulations/eregs-component-lib/src/components/*.vue
	cd ui/regulations/eregs-component-lib; \
		npm run build;

.PHONY: build-spa
build-spa: ## Build vite assets
build-spa:
	cd ui/regulations/eregs-vite; \
		npm run build;

.PHONY: watch-css
watch-css: ## Watch regulations static assets and rebuild when they're changed
watch-css:
	cd ui/regulations; \
		(trap 'kill 0' SIGINT; npm run watch-css);

.PHONY: watch-spa
watch-spa: ## Watch vite components
watch-spa:
	cd ui/regulations/eregs-vite; \
		(trap 'kill 0' SIGINT; npm run watch-build);

.PHONY: watch-eregs-component-lib
watch-component-lib: ## Watch eregs component library components
watch-component-lib:
	cd ui/regulations/eregs-component-lib; \
		(trap 'kill 0' SIGINT; npm run watch-build:components);

.PHONY: watch-eregs-main
watch-eregs-main: ## Watch eregs main.js
watch-eregs-main:
	cd ui/regulations/eregs-component-lib; \
		(trap 'kill 0' SIGINT; node watch-dist.js);

.PHONY: watch
watch: ## watch non-SPA pages for changes
watch:
	${MAKE} -j4 watch-css watch-component-lib watch-eregs-main

.PHONY: watch-all
watch-all: ## watch everything for changes
watch-all:
	${MAKE} -j4 watch-css watch-component-lib watch-eregs-main watch-spa

.PHONY: storybook
storybook: ## Run storybook for regulations
storybook: ui/regulations/.storybook
	cd ui/regulations; \
		npm install; \
		npm run storybook

.PHONY: prototype
prototype: ## Run prototype for regulations
prototype: ui/prototype
	cd ui/prototype; \
		npm run start-container

prototype.clean: ## Stop prototype for regulations
prototype.clean: ui/prototype
	cd ui/prototype; \
		npm run stop-container

.PHONY: lint
lint:
	flake8;
ruff:
	docker-compose exec regulations ruff check .
ruff-fix:
	docker-compose exec regulations ruff --fix .

local: ## Start a local environment with parts 400 and 433 loaded.
local: regulations local.docker data.local
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

%.prod: ## Load a Part of Title 42. e.g. make data.prod.435 will load Part 435 into prod
%.prod: CORE_URL = https://3iok6sq3ui.execute-api.us-east-1.amazonaws.com/prod/v3/

%.val: ## Load a Part of Title 42. e.g. make data.val.435 will load Part 435 into val
%.val: CORE_URL = https://qavc1ytrff.execute-api.us-east-1.amazonaws.com/val/v3/

%.dev: ## Load a Part of Title 42. e.g. make dev.data.435 will load Part 435 into dev
%.dev: CORE_URL = https://hittwbzqah.execute-api.us-east-1.amazonaws.com/dev/v3/

%.experimental: ## Load a Part of Title 42. e.g. make data.experimental URL=[experimental lambda URL] into dev-experimental
%.experimental: CORE_URL = $(URL)/v3/

%.local: ## Load a Part of Title 42. e.g. make data.local.435 will load Part 435
%.local: CORE_URL = http://localhost:8000/v3/
%.local: export EREGS_USERNAME=RpSS01rhbx
%.local: export EREGS_PASSWORD=UkOAsfkItN

data.%:
	EREGS_API_URL_V3=$(CORE_URL) docker-compose -f docker-compose.yml -f docker-compose.parser.yml up parser

frdocs.%:
	EREGS_API_URL_V3=$(CORE_URL) docker-compose -f docker-compose.yml -f docker-compose.fr-parser.yml up fr-parser

local.stop: ## Stop the local environment, freeing up resources and ports without destroying data.
	docker-compose stop

local.start: ## Start the local environment if stopped using `make local.stop`
	docker-compose start

local.clean: ## Remove the local environment entirely.
	docker-compose down --remove-orphans --volumes

local.createadmin: ## Create a local admin account.
	docker-compose exec regulations python manage.py createsuperuser

local.collectstatic: ## Create static assets.
	docker-compose exec regulations python manage.py collectstatic --noinput

local.opensearch: ## Run a local opensearch environment
	docker-compose -f docker-compose.opensearch.yml up -d

test.cypress: ## run the cypress e2e suite
	DJANGO_SETTINGS_MODULE="cmcs_regulations.settings.test_settings" docker-compose -f docker-compose.yml  -f docker-compose.e2e.yml up e2e
test.cypress.local: ## run cypress tests locally without docker
	cd ui/e2e; \
		npm install; \
		npm run cypress:run;
.PHONY: test.vite
test.vitest:
	cd ui/regulations;\
		npm install;\
		npm run test-vue;
test.vitest.coverage:
	cd ui/regulations;\
		npm install;\
		npm run test-vue-coverage;
		
python.unittest:
	docker-compose exec regulations python manage.py test 

##uncomment the -vvv if there are errors running pytest. 
test.pytest:
	DJANGO_SETTINGS_MODULE="cmcs_regulations.settings.test_settings" docker-compose -f docker-compose.yml exec regulations pytest -vvv 

python.shell:
	docker-compose exec regulations python manage.py shell

python.emptyseedtables:
	docker-compose exec regulations python manage.py emptyseedtables

python.makemigrations:
	docker-compose exec regulations python manage.py makemigrations

python.migrate:
	docker-compose exec regulations python manage.py migrate

objects = resources.abstractcategory resources.category resources.subcategory resources.abstractlocation resources.section resources.subpart resources.federalregisterdocumentgroup resources.resourcesconfiguration resources.abstractresource resources.federalregisterdocument resources.supplementalcontent

local.seed:
	$(foreach object, $(objects), docker-compose exec regulations python manage.py loaddata $(object).json;) \
	docker-compose exec regulations python manage.py loaddata search.synonym.json 
	docker-compose exec regulations python manage.py loaddata regulations.statutelinkconverter.json

local.dump:
	$(foreach object, $(objects), docker-compose exec regulations python manage.py dumpdata $(object) --indent 4 > ./backend/resources/fixtures/$(object).json;) \
	docker-compose exec regulations python manage.py dumpdata search.synonym --indent 4 > ./backend/regcore/search/fixtures/search.synonym.json
	docker-compose exec regulations python manage.py dumpdata regulations.statutelinkconverter --indent 4 > ./backend/regulations/fixtures/regulations.statutelinkconverter.json

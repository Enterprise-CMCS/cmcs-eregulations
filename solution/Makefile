.PHONY: help
help: ## Show this help.
	@egrep '^[a-zA-Z_\.%-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

regulations: ## Build regulations assets
regulations: ui/regulations/node_modules static-assets/regulations/css/main.css ui/regulations/eregs-component-lib/node_modules static-assets/regulations/js/eregs-main.iife.js ui/regulations/eregs-vite/node_modules build-spa

install-npm: ## Install npm dependencies
install-npm: ui/regulations/node_modules ui/regulations/eregs-vite/node_modules ui/regulations/eregs-component-lib/node_modules

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

.PHONY: watch-text-extractor
watch-text-extractor: ## Watch text extractor lambda for changes
watch-text-extractor:
	watchfiles --filter python 'make text-extractor.restart'

.PHONY: watch
watch: ## watch non-SPA pages for changes
watch:
	${MAKE} -j4 watch-css watch-component-lib watch-eregs-main

.PHONY: watch-all
watch-all: ## watch everything for changes
watch-all:
	${MAKE} -j4 watch-css watch-component-lib watch-eregs-main watch-spa watch-text-extractor

.PHONY: eslint-frontend
eslint-frontend: ## Run eslint
	cd ui/regulations; \
		npm install; \
		npm run eslint;

.PHONY: eslint-cdk
eslint-cdk: ## Run eslint
	cd ../cdk-eregs; \
		npm install; \
		npm run eslint;

.PHONY: lint
lint:
	flake8;
ruff:
	docker compose exec regulations ruff check --preview .
	docker compose exec text-extractor ruff check --preview .
ruff-fix:
	docker compose exec regulations ruff check --preview --fix .
	docker compose exec text-extractor ruff check --preview --fix .
local: ## Start a local environment with parts 400 and 433 loaded.
local: regulations local.docker data.local
	@echo Local environment started. Visit http://localhost:8000

local.docker: ## Start a local environment
local.docker:
	docker compose up -d; \
		sleep 5; \
		make local.regulations;

local.regulations: ## Run migrations and restart the regulations-core
	docker compose exec regulations python manage.py migrate; \
		docker compose restart regulations; \
		sleep 5;
local.spectacular: ## Run swagger locally 
	docker compose exec regulations python manage.py spectacular --file schema.yaml

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
	EREGS_API_URL_V3=$(CORE_URL) docker compose -f docker-compose.yml -f docker-compose.parser.yml up parser

frdocs.%:
	EREGS_API_URL_V3=$(CORE_URL) docker compose -f docker-compose.yml -f docker-compose.fr-parser.yml up fr-parser

local.stop: ## Stop the local environment, freeing up resources and ports without destroying data.
	docker compose stop

local.start: ## Start the local environment if stopped using `make local.stop`
	docker compose start

local.clean: ## Remove the local environment entirely.
	docker compose down --remove-orphans --volumes

local.createadmin: ## Create a local admin account.
	docker compose exec regulations python manage.py createsuperuser

local.collectstatic: ## Create static assets.
	docker compose exec regulations python manage.py collectstatic --noinput

local.opensearch: ## Run a local opensearch environment
	docker compose -f docker-compose.opensearch.yml up -d

test.cypress: ## run the cypress e2e suite
	DJANGO_SETTINGS_MODULE="cmcs_regulations.settings.test_settings" docker compose -f docker-compose.yml  -f docker-compose.e2e.yml up e2e
	docker compose -f docker-compose.yml up -d ## resets the django_settings_module to the default
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
test.vitest.ui:
	cd ui/regulations;\
		npm install;\
		npm run test-vue-ui;

##uncomment the -vvv if there are errors running pytest. 
test.pytest:
	DJANGO_SETTINGS_MODULE="cmcs_regulations.settings.test_settings" docker compose -f docker-compose.yml up -d
	docker compose exec regulations pytest -v
	docker compose -f docker-compose.yml up -d  ## resets the django_settings_module to the default
test.pytest.cov:
	DJANGO_SETTINGS_MODULE="cmcs_regulations.settings.test_settings" docker compose -f docker-compose.yml up -d
	docker compose exec regulations pytest --cov
	docker compose -f docker-compose.yml up -d  ## resets the django_settings_module to the default
python.shell:
	docker compose exec regulations python manage.py shell

python.emptyseedtables:
	docker compose exec regulations python manage.py emptyseedtables

python.makemigrations:
	docker compose exec regulations python manage.py makemigrations

python.migrate:
	docker compose exec regulations python manage.py migrate

local.seed:
	docker compose exec regulations python manage.py populateseeddata
	docker compose exec regulations python manage.py index_resources

local.cleanseeddata:
	docker compose exec regulations python manage.py cleanseeddata

text-extractor:
	docker compose up -d --build text-extractor

text-extractor.stop:
	docker compose stop text-extractor

text-extractor.start:
	docker compose start text-extractor

text-extractor.restart:
	make text-extractor.stop; make text-extractor.start

text-extractor.test:
	docker compose exec text-extractor sh -c 'cd app; python -m unittest'

# Do not change the order of these objects.  In some cases it matters
resource_objects = resources.abstractcategory resources.category resources.subcategory resources.abstractlocation resources.section resources.subpart resources.federalregisterdocumentgroup resources.resourcesconfiguration resources.abstractresource resources.federalregisterdocument resources.supplementalcontent
reg_objects = regulations.siteconfiguration regulations.statutelinkconfiguration regulations.statutelinkconverter regulations.regulationlinkconfiguration
file_manager_objects = file_manager.subject
auth_objects = contenttypes.contenttype auth.permission auth.group

local.dump:
	$(foreach object, $(resource_objects), docker compose exec regulations python manage.py dumpdata $(object) --indent 4 > ./backend/resources/fixtures/$(object).json;) \
	$(foreach object, $(reg_objects), docker compose exec regulations python manage.py dumpdata $(object) --indent 4 > ./backend/regulations/fixtures/$(object).json;) \
	$(foreach object, $(file_manager_objects), docker compose exec regulations python manage.py dumpdata $(object) --indent 4 > ./backend/file_manager/fixtures/$(object).json;) \
	$(foreach object, $(auth_objects), docker compose exec regulations python manage.py dumpdata $(object) --indent 4 > ./backend/cmcs_regulations/fixtures/$(object).json;) \
	docker compose exec regulations python manage.py dumpdata contenttypes.contenttype --indent 4 > ./backend/cmcs_regulations/fixtures/contenttypes.contenttype.json
	docker compose exec regulations python manage.py dumpdata search.synonym --indent 4 > ./backend/regcore/search/fixtures/search.synonym.json 

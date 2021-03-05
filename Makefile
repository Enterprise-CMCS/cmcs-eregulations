
regulations-site: regulations-site/regulations/static/regulations/css/main.css
regulations-site/regulations/static/regulations/css/main.css: regulations-site/regulations/static/regulations/css/**/*.scss
	cd regulations-site/regulations/static; \
		npm run css;

.PHONY: watch
watch:
	cd regulations-site/regulations/static; \
		npm run watch-css;

.PHONY: sync
sync:
	git submodules update --init

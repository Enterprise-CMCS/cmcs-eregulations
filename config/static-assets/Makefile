dir := ${CURDIR}

node_modules:
	npm install

static:
	cp -r ../regulations-site/regulations/static .

config.json:
	echo {\"frontEndPath\": \"$(dir)/static/regulations\"} > config.json

build: static node_modules config.json
	npx grunt

clean:
	rm -r static

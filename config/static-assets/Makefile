dir := ${CURDIR}

node_modules:
	npm install

config.json:
	echo {\"frontEndPath\": \"$(dir)/static/regulations\"} > config.json

build: node_modules config.json
	npx grunt

dir != pwd

node_modules:
	npm install

static:
	cp -r ../regulations/static .

config.json:
	echo {\"frontEndPath\": \"$(dir)/static\"} > config.json

build: static node_modules config.json
	npx grunt

clean:
	rm -r static

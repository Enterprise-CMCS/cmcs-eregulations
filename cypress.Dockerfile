FROM cypress/included:9.1.1

WORKDIR ./app
COPY ./e2e/package.json ./
COPY ./e2e/package-lock.json ./

RUN npm install

copy ./e2e ./
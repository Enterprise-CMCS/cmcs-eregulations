FROM cypress/base:10
RUN npm install --save-dev cypress

COPY ["cypress.json", "/app/e2e/cypress.json"]
COPY ["cypress", "/app/e2e/cypress"]

WORKDIR /app/e2e/
RUN npx cypress verify

CMD npx cypress run

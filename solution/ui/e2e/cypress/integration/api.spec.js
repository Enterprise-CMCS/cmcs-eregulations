const TITLE = 42;
const SUBPART = "A";
const PART = 430;
const SECTION = 10;
const VERSION = "latest";
const SYNONYM = "synonym";
const SEARCH_TERM = "a+search+term";

const API_ENDPOINTS_V3 = [
    `/v3/ecfr_parser_result/${TITLE}`,
    `/v3/parser_config`,
    `/v3/resources/`,
    `/v3/resources/categories`,
    `/v3/resources/categories/tree`,
    `/v3/resources/federal_register_docs`,
    `/v3/resources/federal_register_docs/doc_numbers`,
    `/v3/resources/locations`,
    `/v3/resources/locations/sections`,
    `/v3/resources/locations/subparts`,
    `/v3/resources/supplemental_content`,
    `/v3/synonym/${SYNONYM}`,
    `/v3/title/${TITLE}/part/${PART}/version/${VERSION}`,
    `/v3/title/${TITLE}/part/${PART}/version/${VERSION}/section/${SECTION}`,
    `/v3/title/${TITLE}/part/${PART}/version/${VERSION}/sections`,
    `/v3/title/${TITLE}/part/${PART}/version/${VERSION}/subpart/${SUBPART}`,
    `/v3/title/${TITLE}/part/${PART}/version/${VERSION}/subpart/${SUBPART}/toc`,
    `/v3/title/${TITLE}/part/${PART}/version/${VERSION}/subparts`,
    `/v3/title/${TITLE}/part/${PART}/version/${VERSION}/toc`,
    `/v3/title/${TITLE}/part/${PART}/versions`,
    `/v3/title/${TITLE}/parts`,
    `/v3/title/${TITLE}/versions`,
    `/v3/title/${TITLE}/toc`,
    `/v3/titles`,
    `/v3/toc`,
    `/v3/search?q=${SEARCH_TERM}`,
];

describe("API testing", () => {
    API_ENDPOINTS_V3.forEach(endpoint => {
        it(`sends GET request to ${endpoint} and checks for a 200 response`, () => {
            cy.request(endpoint).as("request");
            cy.get("@request").then((response) => {
                cy.log(`${endpoint} - ${response.status}`);
                expect(response.status).to.eq(200);
            });
        });
    });
});

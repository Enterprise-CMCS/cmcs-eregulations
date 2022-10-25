const TITLE = 42;
const SUBPART = "A";
const PART = 430;
const SECTION = 10;
const VERSION = "latest";
const SYNONYM = "synonym";

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
        it(`returns results for GET request to a title with no locations`, () => {
            let endpoint = "v3/resources/?&category_details=true&location_details=true&start=undefined&max_results=1000&q=\"Identifying%20Medicaid%20and%20CHIP%20Beneficiaries\"&sort=newest&paginate=true&page_size=100&page=1&fr_grouping=false"
            cy.request(endpoint).as("request");
            cy.get("@request").then((response) => {
                cy.log(`${endpoint} - ${response.status}`);
                cy.log(`${response}`)
                expect(response.body.count).to.greaterThan(0)
                expect(response.status).to.eq(200);
            });
        });
    });
});

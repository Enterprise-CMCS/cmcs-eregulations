const TITLE = 42;
const SUBPART = "A";
const PART = 430;
const SECTION = 10;
const VERSION = "latest";
const SEARCH_TERM = "FMAP";
const ACT = "Social Security Act";
const PATTERN = "1903";

// TODO: uncomment this and point it at the new synonyms endpoint under content-search
// const SYNONYMS_ENDPOINT = "/v3/synonyms?q=";
// const SPECIAL_CHARACTERS = [
//     "%",
//     "138% FPL",
//     "138 % FPL",
//     '"',
//     '""',
//     "#",
//     ".",
//     "..",
//     "?",
// ];

const API_ENDPOINTS_V3 = [
    `/v3/acts`,
    `/v3/statute-link/?pattern=${PATTERN}`,
    `/v3/content-search?q=${SEARCH_TERM}`,
    `/v3/content-search/counts?q=${SEARCH_TERM}`,
    `/v3/ecfr_parser_result/${TITLE}`,
    `/v3/parser_config`,
    `/v3/resources/`,
    `/v3/resources/citations`,
    `/v3/resources/citations/sections`,
    `/v3/resources/citations/subparts`,
    `/v3/resources/internal`,
    `/v3/resources/internal/categories`,
    `/v3/resources/internal/files`,
    `/v3/resources/internal/links`,
    `/v3/resources/public`,
    `/v3/resources/public/categories`,
    `/v3/resources/public/federal_register_links`,
    `/v3/resources/public/links`,
    `/v3/resources/subjects`,
    `/v3/statutes`,
    `/v3/statutes?act=${ACT}`,
    //`${SYNONYMS_ENDPOINT}${SYNONYM}`,  // TODO: see above
    //`/v3/title/${TITLE}/part/${PART}/history/section/${SECTION}`,
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
    API_ENDPOINTS_V3.forEach((endpoint) => {
        it(`sends GET request to ${endpoint} and checks for a 200 or 403 (Forbidden) response`, () => {
            cy.request({ url: endpoint, failOnStatusCode: false }).as(
                "request"
            );
            cy.get("@request").then((response) => {
                cy.log(`${endpoint} - ${response.status}`);
                expect(response.status).to.be.oneOf([200, 403]);
            });
        });
    });
});

// TODO: re-enable this test and point it at the new synonyms endpoint under content-search
// describe("Synonyms endpoint special character testing", () => {
//     SPECIAL_CHARACTERS.forEach((character) => {
//         const endpoint = SYNONYMS_ENDPOINT + encodeURIComponent(character);
//         it(`sends GET request to ${endpoint} and checks for a 200 response`, () => {
//             cy.request({ url: endpoint }).as("request");
//             cy.get("@request").then((response) => {
//                 cy.log(`${endpoint} - ${response.status}`);
//                 expect(response.status).to.eq(200);
//             });
//         });
//     });
// });

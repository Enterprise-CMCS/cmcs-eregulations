const SEARCH_TERM = "FMAP";
const SEARCH_TERM2 = "medicaid";
describe("Search flow", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("has a working search box on the homepage on desktop", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".header--search > form > input")
            .should("be.visible")
            .should("have.attr", "placeholder", "Search")
            .type(`${SEARCH_TERM}`);
        cy.get(".header--search > form").submit();

        cy.url().should("include", `/search/?q=${SEARCH_TERM}`);
    });

    it("has a working search box on the desktop on mobile when search open icon is clicked", () => {
        cy.viewport("iphone-x");
        cy.visit("/42/430/");
        cy.get("button.form__button--toggle-mobile-search")
            .should("be.visible")
            .click({ force: true });
        cy.get(".header--search > form > input")
            .should("be.visible")
            .type(`${SEARCH_TERM}`);

        cy.get(".header--search > form").submit();

        cy.url().should("include", `/search/?q=${SEARCH_TERM}`);
    });

    it("should have a valid link to medicaid.gov", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.get(".options-list li:nth-child(3) a")
            .should("have.attr", "href")
            .and("include", "search-gsc");
    });

    it("checks a11y for search page", () => {
        cy.viewport("macbook-15");
        cy.visit("/search/?q=FMAP", { timeout: 60000 });
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("should have a working searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search`, { timeout: 60000 });
        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get(".search-field .v-input__icon--append button").click({
            force: true,
        });
        cy.url().should("include", "/search?q=test");
    });

    it("should be able to clear the searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });

        cy.get(".search-field .v-input__icon--clear button").click({
            force: true,
        });

        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });

        cy.findByDisplayValue("test")
            .should("be.visible")
            .should("have.value", "test");

        cy.get("input#main-content").clear();

        cy.get("input#main-content").should("have.value", "");
    });

    it("switches to our meta data when search.gov returns nothing", () => {
        cy.intercept(`**/v3/resources/search?q=${SEARCH_TERM2}**page=1**`, {
            fixture: "no-resources-results.json",
            statusCode: 400,
        }).as("resources");
        cy.intercept(`**/v3/resources/?&**${SEARCH_TERM2}**page=1**`, {
            fixture: "meta-data.json"
        }).as("metadata");
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM2}`, { timeout: 60000 });
        cy.wait("@resources");

        cy.get(".reg-results-content .search-results-count > h2").should(
            "have.text",
            "Regulations"
        );
        cy.get(".reg-results-content .search-results-count > span").should(
            "be.visible"
        );
        cy.get(".resources-results-content .search-results-count > h2").should(
            "have.text",
            "Resources"
        );
        cy.get(".resources-results-content .search-results-count > span > span").should(
            "have.text",
            " 1 - 1 of "
        );
        cy.get(
            ".resources-results-content .search-results-count > span"
        ).should("be.visible");
        cy.get(
            ".reg-results-content .reg-results-container .result:nth-child(1) .result__link"
        ).should("be.visible");
        cy.get(
            ".reg-results-content .reg-results-container .result:nth-child(1) .result__link a"
        ).should("have.attr", "href");
    });

    it("should return no resoures when going on page 3 without enough resources returned", () => {
        cy.intercept(`**/v3/resources/search?q=${SEARCH_TERM2}**page=3**`, {
            fixture: "search-gov-not-enough.json",
            statusCode: 400,
        }).as("resources");
        // this call is never executed since the conditional in js will not call it.
        cy.intercept(`**/v3/resources/?&**${SEARCH_TERM2}**page=3**`, {
            fixture: "meta-data.json"
        }).as("metadata");
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM2}&page=3`, { timeout: 60000 });
        cy.wait("@resources");

        cy.get(".reg-results-content .search-results-count > h2").should(
            "have.text",
            "Regulations"
        );
        cy.get(".reg-results-content .search-results-count > span").should(
            "be.visible"
        );
        cy.get(".resources-results-content .search-results-count > h2").should(
            "have.text",
            "Resources"
        );
        cy.get(".resources-results-content .search-results-count > span").should(
            "have.text",
            " 0 results"
        );
        cy.get(
            ".resources-results-content .search-results-count > span"
        ).should("be.visible");
        cy.get(
            ".reg-results-content .reg-results-container .result:nth-child(1) .result__link"
        ).should("be.visible");
        cy.get(
            ".reg-results-content .reg-results-container .result:nth-child(1) .result__link a"
        ).should("have.attr", "href");
    });

    it("displays results of the search and highlights search term in regulation text", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.get(".reg-results-content .search-results-count > h2").should(
            "have.text",
            "Regulations"
        );
        cy.get(".reg-results-content .search-results-count > span").should(
            "be.visible"
        );
        cy.get(".resources-results-content .search-results-count > h2").should(
            "have.text",
            "Resources"
        );
        cy.get(
            ".resources-results-content .search-results-count > span"
        ).should("be.visible");
        cy.get(
            ".reg-results-content .reg-results-container .result:nth-child(1) .result__link"
        ).should("be.visible");
        cy.get(
            ".reg-results-content .reg-results-container .result:nth-child(1) .result__link a"
        ).should("have.attr", "href");
        cy.get(
            ".reg-results-content .reg-results-container .result:nth-child(1) .result__link a"
        ).click({ force: true });
        cy.url().should(
            "include",
            `${SEARCH_TERM}#`
        );
        cy.focused().then(($el) => {
            cy.get($el).within(($focusedEl) => {
                cy.get("mark.highlight")
                    .contains(`${SEARCH_TERM}`)
                    .should(
                        "have.css",
                        "background-color",
                        "rgb(252, 229, 175)"
                    );
            });
        });
    });
});

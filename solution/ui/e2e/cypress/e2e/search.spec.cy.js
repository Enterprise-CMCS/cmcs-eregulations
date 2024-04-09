const SEARCH_TERM = "FMAP";

const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

describe("Search flow", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("has a working search box on the homepage on desktop", () => {
        cy.clearIndexedDB();
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

    it("checks a11y for search page", () => {
        cy.viewport("macbook-15");
        cy.visit("/search/?q=FMAP", { timeout: 60000 });
        cy.checkLinkRel();
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("should have a working searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search`, { timeout: 60000 });
        cy.get("input#main-content")
            .should("be.visible")
            .type("test search", { force: true });
        cy.get('[data-cy="search-form-submit"]').click({
            force: true,
        });
        cy.url().should("include", "/search?q=test+search");
        cy.get(".search-form .form-helper-text .search-suggestion").should(
            "not.exist"
        );
    });

    it("should be able to clear the searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });

        cy.get('[data-cy="clear-search-form"]').click({
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

    it("should have the correct labels for public and internal documents", () => {
        cy.checkPolicyDocs({
            username,
            password,
            landingPage: "/search/",
        });
    });

    it("should go to the Subjects page with a selected subject when a subject chip is clicked", () => {
        cy.intercept("**/v3/content-search/**", {
            fixture: "policy-docs.json",
        }).as("subjectFiles");

        cy.intercept("**/v3/file-manager/subjects", {
            fixture: "subjects.json",
        }).as("subjects");

        cy.viewport("macbook-15");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/search/",
        });

        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get('[data-cy="search-form-submit"]').click({
            force: true,
        });

        cy.get(`a[data-testid=add-subject-chip-3]`).click({
            force: true,
        });

        cy.url().should("include", "/subjects/?subjects=3");
        cy.get(".subject__heading")
            .should("exist")
            .and("have.text", "Access to Services");
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
        cy.url().should("include", `${SEARCH_TERM}#`);
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

    it("should have a valid link to medicaid.gov", () => {
        cy.clearIndexedDB();
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.get(".options-list li:nth-child(3) a")
            .should("have.attr", "href")
            .and("include", "search-gsc");
    });

    it("should have the correct error message when the the resources column throws an error", () => {
        cy.clearIndexedDB();

        cy.intercept("**/v3/content-search/**", {
            statusCode: 500,
        }).as("resourcesError");

        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });

        cy.get(
            ".resources-results-content .resources-count__span--error"
        ).should(
            "have.text",
            "We're unable to display results for this query right now"
        );

        cy.get(".reg-results-content .error__msg").should("not.exist");

        cy.get(".resources-results-content .error__msg").should(
            "have.text",
            "Please try a different query, try again later, or let us know."
        );

        cy.get(".reg-results-content .options-list li:nth-child(3) a").should(
            "not.exist"
        );

        cy.get(".resources-results-content .options-list li:nth-child(3) a")
            .should("have.attr", "href")
            .and("include", "search-gsc");
    });

    it("should have the correct error message when the the regulations column throws an error", () => {
        cy.clearIndexedDB();

        cy.intercept("**/v3/search/**", {
            statusCode: 500,
        }).as("resourcesError");

        cy.intercept("**/v3/content-search/**", {
            fixture: "policy-docs.json",
        }).as("subjectFiles");

        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });

        cy.get(".reg-results-content .regs-count__span--error").should(
            "have.text",
            "We're unable to display results for this query right now"
        );

        cy.get(".resources-results-content .error__msg").should("not.exist");

        cy.get(".reg-results-content .error__msg").should(
            "have.text",
            "Please try a different query, try again later, or let us know."
        );

        cy.get(
            ".resources-results-content .options-list li:nth-child(3) a"
        ).should("not.exist");

        cy.get(".reg-results-content .options-list li:nth-child(3) a")
            .should("have.attr", "href")
            .and("include", "search-gsc");
    });
});

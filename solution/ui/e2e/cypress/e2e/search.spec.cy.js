const SEARCH_TERM = "FMAP";
const SEARCH_TERM_2 = "almond";

const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

describe("Search flow", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept("**/v3/content-search/**", {
            fixture: "policy-docs-search.json",
        }).as("subjectFiles");

        cy.intercept("**/v3/resources/subjects**", {
            fixture: "subjects.json",
        }).as("subjects");

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
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });
        cy.url().should("include", "/search?q=test+search");
    });

    it("should be able to clear the searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });

        cy.url().should("include", `/search/?q=${SEARCH_TERM}`);

        cy.get('[data-testid="clear-search-form"]').click({
            force: true,
        });

        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });

        cy.findByDisplayValue("test")
            .should("be.visible")
            .should("have.value", "test");

        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        cy.url().should("include", "/search?q=test");

        cy.get("input#main-content").clear();

        cy.get("input#main-content").should("have.value", "");

        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        cy.url().should("not.include", "test");
    });

    it("should have the correct labels for public, regulations, and internal documents", () => {
        cy.checkPolicyDocs({
            username,
            password,
            landingPage: "/search/",
        });
    });

    it("should go to the Subjects page with a selected subject when a subject chip is clicked", () => {
        cy.viewport("macbook-15");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/search/",
        });

        cy.get("input#main-content")
            .should("be.visible")
            .type(`${SEARCH_TERM_2}`, { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        cy.get(`a[data-testid=add-subject-chip-9]`).first().click({
            force: true,
        });

        cy.url().should("include", "/subjects/?subjects=9");
        cy.get(".subject__heading")
            .should("exist")
            .and("have.text", "Care Coordination");
    });

    it.skip("displays results of the search and highlights search term in regulation text", () => {
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
});

const TITLE_42 = 42;
const TITLE_45 = 45;

const SEARCH_TERM = "FMAP";
const SEARCH_TERM_2 = "almond";
const NO_RESULTS_SEARCH_TERM = "no results";
const SPACED_SEARCH_TERM = "test query";
const QUOTED_SEARCH_TERM = '"test query"';

const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

describe("Search flow", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept("**/v3/titles", [TITLE_42, TITLE_45]).as("titles");

        cy.intercept(`**/v3/content-search/**`, {
            fixture: "policy-docs-search.json",
        }).as("subjectFiles");

        cy.intercept("**/v3/title/${TITLE_42}/parts", {
            fixture: "parts-42.json",
        }).as("parts42");

        cy.intercept(`**/v3/title/${TITLE_45}/parts`, {
            fixture: "parts-45.json",
        }).as("parts45");

        cy.intercept("**/v3/resources/subjects**", {
            fixture: "subjects.json",
        }).as("subjects");

        cy.intercept("**/v3/resources/internal/categories**", {
            fixture: "categories-internal.json",
        }).as("internalCategories");

        cy.intercept("**/v3/resources/public/categories**", {
            fixture: "categories.json",
        }).as("categories");

        cy.intercept(`**/v3/content-search/counts**`, {
            fixture: "counts.json",
        }).as("counts");
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
            .should("exist")
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
            .should("exist")
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
            .should("exist")
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

    it("should not show internal checkbox when not logged in", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("label")
            .should("have.text", "Regulations");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("label")
            .should("have.text", "Public Resources");
        cy.get(".doc-type__toggle fieldset > div").eq(2).should("not.exist");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/search/",
        });

        cy.get("input#main-content")
            .should("exist")
            .type(`${SEARCH_TERM}`, { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        cy.get(".doc-type__toggle fieldset > div")
            .eq(2)
            .find("label")
            .should("have.text", "Internal Resources(1)");
    });

    it("should not show the categories or subjects dropdowns when only regulations are selected", () => {
        cy.viewport("macbook-15");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/search/",
        });

        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.get("div[data-testid='category-select']").should("be.visible");
        cy.get("button[data-testid='subjects-activator']").should("be.visible");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .check({ force: true });
        cy.get("div[data-testid='category-select']").should("not.be.visible");
        cy.get("button[data-testid='subjects-activator']").should(
            "not.be.visible",
        );
        cy.get(".doc-type__toggle fieldset > div");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .check({ force: true });
        cy.get("div[data-testid='category-select']").should("be.visible");
        cy.get("button[data-testid='subjects-activator']").should("be.visible");
    });

    it("has the correct type params in URL for each doc type combination", () => {
        cy.viewport("macbook-15");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/search/",
        });

        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });

        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .check({ force: true });

        cy.url().should("include", `/search?q=${SEARCH_TERM}&type=regulations`);
        cy.url().should("not.include", "external");
        cy.url().should("not.include", "internal");

        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .check({ force: true });

        cy.url().should(
            "include",
            `/search?q=${SEARCH_TERM}&type=regulations,external`,
        );
        cy.url().should("not.include", "internal");

        cy.get(".doc-type__toggle fieldset > div")
            .eq(2)
            .find("input")
            .check({ force: true });

        cy.url().should(
            "include",
            `/search?q=${SEARCH_TERM}&type=regulations,external,internal`,
        );
    });

    it("category should be selected on load if included in URL", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search?q={SEARCH_TERM}&categories=3`);
        cy.get("div[data-testid='category-select']")
            .should("exist")
            .find(".v-select__selection")
            .should("have.text", "Related Regulations Fixture Item");
    });

    it("subject should be selected on load if included in the URL", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search?q={SEARCH_TERM}&subjects=2`);
        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .find(".subjects-select__label")
            .should("have.text", "ABP")
            .click({ force: true });

        cy.get("button[data-testid=add-subject-2]").should(
            "have.class",
            "subjects-li__button--selected",
        );
    });

    it("subject should change in URL if new subject is selected from the Subjects dropdown", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search?q=${SEARCH_TERM}&subjects=2`);

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .find(".subjects-select__label")
            .should("have.text", "ABP")
            .click({ force: true });

        cy.get("button[data-testid=add-subject-3]")
            .should("not.have.class", "subjects-li__button--selected")
            .find(".count")
            .should("have.text", "(15)");

        cy.get("button[data-testid=add-subject-3]").click({ force: true });

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .find(".subjects-select__label")
            .should("have.text", "Access to Services")
            .click({ force: true });

        cy.get("button[data-testid=add-subject-2]").should(
            "not.have.class",
            "subjects-li__button--selected",
        );

        cy.get("button[data-testid=add-subject-3]").should(
            "have.class",
            "subjects-li__button--selected",
        );

        cy.url().should("include", "subjects=3");
    });

    it("subjects and categories can be selected simultaneously", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search?q=${SEARCH_TERM}`);

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .click();

        cy.get("button[data-testid=add-subject-3]").click({ force: true });

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .find(".subjects-select__label")
            .should("have.text", "Access to Services")
            .click({ force: true });

        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']").click({ force: true });

        cy.get("div[data-testid='category-select']")
            .find(".v-select__selection")
            .should("have.text", "Related Statutes in Fixture");

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .find(".subjects-select__label")
            .should("have.text", "Access to Services");

        cy.url().should("include", "subjects=3").and("include", "categories=1");
    });

    it("subjects can be cleared by clicking the clear button", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search?q=${SEARCH_TERM}`);

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .click();

        cy.get("button[data-testid=add-subject-3]").click({ force: true });

        cy.url().should("include", "subjects=3");

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .find(".subjects-select__label")
            .should("have.text", "Access to Services")
            .click({ force: true });

        cy.get("i[data-testid='subjects-select-clear']").click({ force: true });

        cy.get("button[data-testid='subjects-activator']")
            .should("exist")
            .find(".subjects-select__label")
            .should("have.text", "Choose Subject");

        cy.url().should("not.include", "subjects=3");

    });

    it("displays results of the search and highlights search term in regulation text", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.get("a.document__link--regulations")
            .should("have.attr", "href")
            .and("include", `${SEARCH_TERM}#435-928`);
        cy.get("a.document__link--regulations").click({ force: true });
        cy.url().should("include", `${SEARCH_TERM}#435-928`);
        cy.focused().then(($el) => {
            cy.get($el).within((_$focusedEl) => {
                cy.get("mark.highlight")
                    .contains(`${SEARCH_TERM}`)
                    .should(
                        "have.css",
                        "background-color",
                        "rgb(252, 229, 175)",
                    );
            });
        });
    });

    it("shows the appropriate messages when there are no search results", () => {
        cy.intercept(`**/v3/content-search/**`, {
            next: null,
            previous: null,
            count: 0,
            results: [],
        }).as("noResults");

        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${NO_RESULTS_SEARCH_TERM}`, { timeout: 60000 });

        cy.get(".no-results__span").should(
            "have.text",
            `Your search for ${NO_RESULTS_SEARCH_TERM} did not match any results on eRegulations.`,
        );

        cy.get("[data-testid=research-row-1]").should("not.exist");

        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .check({ force: true });

        cy.get(".no-results__span").should(
            "have.text",
            `Your search for ${NO_RESULTS_SEARCH_TERM} did not match any results with the selected filters.`,
        );

        cy.get("[data-testid=research-row-1]")
            .should("exist")
            .find("[data-testid=reset-filters-parent] a")
            .should("have.text", " reset all active filters")
            .click({ force: true });

        cy.get(".no-results__span").should(
            "have.text",
            `Your search for ${NO_RESULTS_SEARCH_TERM} did not match any results on eRegulations.`,
        );

        cy.get("[data-testid=research-row-1]").should("not.exist");

        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .should("not.be.checked");
    });

    it("has a Continue Your Research section on the search page", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.get(".research__title").should("exist");
        cy.get(".research__title").should(
            "have.text",
            "Continue Your Research",
        );

        cy.get("[data-testid=research-row-1]").should("not.exist");
        cy.get("[data-testid=research-row-2]").should("exist");
    });

    it("properly quotes searches and updates the Continue Your Research component when quoted", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SPACED_SEARCH_TERM}`, { timeout: 60000 });
        cy.get(".research__title").should("exist");
        cy.get(".research__title").should(
            "have.text",
            "Continue Your Research",
        );

        cy.get("[data-testid=research-row-1]")
            .should("exist")
            .find("[data-testid=quoted-search-link-parent] a")
            .should("exist")
            .and("have.text", '"test query"')
            .click({ force: true });

        cy.url().should("include", "/search?q=%22test+query%22");

        cy.get("[data-testid=research-row-1]").should("not.exist");
    });
});

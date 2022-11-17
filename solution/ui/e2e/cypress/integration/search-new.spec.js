const SEARCH_TERM = "telemedicine";

describe("Search flow", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("shows up on the homepage on desktop", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".search-header > form > input")
            .should("be.visible")
            .type(`${SEARCH_TERM}`);
        cy.get(".search-header > form").submit();

        cy.url().should("include", `/search/?q=${SEARCH_TERM}`);
    });

    it("shows when mobile search open icon is clicked", () => {
        cy.viewport("iphone-x");
        cy.visit("/42/430/");
        cy.get("button#mobile-search-open")
            .should("be.visible")
            .click({ force: true });
        cy.get("form.search-borderless > input")
            .should("be.visible")
            .type(`${SEARCH_TERM}`);

        cy.get("form.search-borderless").submit();

        cy.url().should("include", `/search/?q=${SEARCH_TERM}`);
    });

    it("displays results of the search and highlights search term in regulation text", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });
        cy.findByText(/\d+ results in Medicaid & CHIP Regulations/).should(
            "be.visible"
        );
        cy.findByRole("link", {
            name: "§ 441.535 Assessment of functional need.",
        })
            .should("be.visible")
            .and("have.attr", "href");
        cy.findByRole("link", {
            name: "§ 441.535 Assessment of functional need.",
        }).click({ force: true });
        cy.url().should(
            "include",
            `42/441/Subpart-K/2021-11-05/?highlight=${SEARCH_TERM}#441-535`
        );
        cy.focused().then(($el) => {
            cy.get($el).should("have.id", "441-535");
            cy.get($el).within(($focusedEl) => {
                cy.get("mark.highlight")
                    .contains(`${SEARCH_TERM}`)
                    .should("have.css", "background-color", "rgb(252, 229, 175)");
            });
        });
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
        cy.findByRole("textbox")
            .should("be.visible")
            .type("test", { force: true });
        cy.get(".search-field .v-input__icon--append button").click({ force: true });
        cy.url().should("include", "/search/?q=test");
    });

    it("should be able to clear the searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit(`/search/?q=${SEARCH_TERM}`, { timeout: 60000 });

        cy.get(".search-field .v-input__icon--clear button").click({ force: true });

        cy.findByRole("textbox")
            .should("be.visible")
            .type("test", { force: true });

        cy.findByDisplayValue("test")
            .should("be.visible")
            .should("have.value", "test");

        cy.get(".search-field .v-input__icon--clear button").click({ force: true });

        cy.findByRole("textbox").should("have.value", "");
    });
});

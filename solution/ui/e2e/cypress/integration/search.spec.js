describe("Search flow", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] =
                Cypress.env("DEPLOYING");
        });
    })

    it("shows up on the homepage on desktop", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".search-header > form > input").should("be.visible").type("State");
        cy.get(".search-header > form").submit();

        cy.url().should("include", "/search/?q=State");
    });

    it("shows when mobile search open icon is clicked", () => {
        cy.viewport("iphone-x");
        cy.visit("/42/430/");
        cy.get("button#mobile-search-open")
            .should("be.visible")
            .click({ force: true });
        cy.get("form.search-borderless > input")
            .should("be.visible")
            .type("State");

        cy.get("form.search-borderless").submit();

        cy.url().should("include", "/search/?q=State");
    });

    it("displays results of the search", () => {
        cy.viewport("macbook-15");
        cy.visit("/search/?q=State", { timeout: 60000 });
        cy.findByText(/\d+ results in Medicaid & CHIP Regulations/).should(
            "be.visible"
        );
        cy.findByRole("link", {
            name: "§ 431.958 Definitions and use of terms.",
        })
            .should("be.visible")
            .and("have.attr", "href");
        cy.findByRole("link", {
            name: "§ 431.958 Definitions and use of terms.",
        }).click({ force: true });
        cy.url().should("include", "/431/Subpart-Q/2020-06-30/#431-958");
    });

    it("checks a11y for search page", () => {
        cy.viewport("macbook-15");
        cy.visit("/search/?q=FMAP", { timeout: 60000 });
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("should have a working searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit("/search/?q=State", { timeout: 60000 });
        cy.scrollTo("top");
        cy.get(".search-reset").click({ force: true });
        cy.findByRole("textbox")
            .should("be.visible")
            .type("test", { force: true });
        cy.get("main .search-box").submit();
        cy.url().should("include", "/search/?q=test");
    });

    it("should be able to clear the searchbox", () => {
        cy.viewport("macbook-15");
        cy.visit("/search/?q=State", { timeout: 60000 });
        cy.scrollTo("top");

        cy.get(".search-reset").click({ force: true });

        cy.findByRole("textbox")
            .should("be.visible")
            .type("test", { force: true });

        cy.findByDisplayValue("test")
            .should("be.visible")
            .should("have.value", "test");

        cy.get(".search-reset").click({ force: true });

        cy.findByRole("textbox").should("have.value", "");
    });
});

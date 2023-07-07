describe("Statute Table", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept(`**/v3/statutes`, {
            fixture: "statutes.json",
        }).as("statutes");
    });

    it("checks a11y for search page", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes/", { timeout: 60000 });
        cy.wait("@statutes");
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("goes to statutes page from homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.clickHeaderLink({ page: "Statutes", screen: "wide" });
        cy.url().should("include", "/statutes/");
    });

    it("statutes link nested in a dropdown menu on narrow screen widths", () => {
        cy.viewport("iphone-x");
        cy.visit("/");
        cy.clickHeaderLink({ page: "Statutes", screen: "narrow" });
        cy.url().should("include", "/statutes/");
    });
});

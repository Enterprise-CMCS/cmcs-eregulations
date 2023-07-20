describe("Statute Table", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept(`**/v3/statutes`, {
            fixture: "statutes.json"
        }).as("statutes");
        return;
    });

    it("checks a11y for search page", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes", { timeout: 60000 });
        cy.wait("@statutes");
        cy.injectAxe();
        cy.checkAccessibility();
    });
});

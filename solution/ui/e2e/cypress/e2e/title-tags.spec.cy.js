describe("Updated HTML Title Tags", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("Homepage title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.title().should("eq", "Medicaid & CHIP eRegulations");
    });

    it("Statutes page title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes/");
        cy.title().should(
            "eq",
            "Statute Reference | Medicaid & CHIP eRegulations"
        );
    });
});

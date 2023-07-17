describe("Statute Table", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept(`**/v3/statutes`, {
            fixture: "statutes.json",
        }).as("statutes");
    });

    it("goes to statutes page from homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.clickHeaderLink({ page: "Statutes", screen: "wide" });
        cy.url().should("include", "/statutes/");
    });

    it("displays as a table at widths 1024px wide and greater", () => {
        cy.viewport(1024, 768);
        cy.visit("/statutes");
        cy.get("#statuteTable").should("be.visible");
        cy.get("#statuteList").should("not.exist");
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("displays as a list at widths narrower than 1024px", () => {
        cy.viewport(1023, 768);
        cy.visit("/statutes");
        cy.get("#statuteTable").should("not.exist");
        cy.get("#statuteList").should("be.visible");
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("statutes link nested in a dropdown menu on mobile screen widths", () => {
        cy.viewport("iphone-x");
        cy.visit("/");
        cy.clickHeaderLink({ page: "Statutes", screen: "narrow" });
        cy.url().should("include", "/statutes/");
    });

    it("goes to another SPA page from the statutes page", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes");
        cy.clickHeaderLink({ page: "Resources", screen: "wide" });
        cy.url().should("include", "/resources");
    });
});

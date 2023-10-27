describe("About page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("should have rel='noopener noreferrer' on all external links", () => {
        cy.viewport("macbook-15");
        cy.visit("/about/");
        cy.checkLinkRel();
    });
});

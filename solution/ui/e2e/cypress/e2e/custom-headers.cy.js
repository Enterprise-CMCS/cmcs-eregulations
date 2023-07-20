describe("Custom Request Headers", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] =
                Cypress.env("DEPLOYING");
        }).as("headers");
        return
    });

    it("has custom testing header x-automated-test added to every request", () => {
        cy.viewport("macbook-15");

        // test custom header on explicit URL visit
        cy.visit("/42/433/");
        cy.wait("@headers")
            .its("request.headers")
            .should(
                "have.property",
                "x-automated-test",
                Cypress.env("DEPLOYING")
            );

        // test custom header after form submit directs to new URL
        cy.get(".toc-section-number").contains("433.50").click({ force: true });
        cy.wait("@headers")
            .its("request.headers")
            .should(
                "have.property",
                "x-automated-test",
                Cypress.env("DEPLOYING")
            );
    });
});

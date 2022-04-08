describe("Print Styles", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        }).as("headers");
    });

    it("has a print button in subpart view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/Subpart-A/2021-03-01/");
        cy.window().then((win) => {
            cy.stub(win, "print");
            cy.get(".print-btn").contains("Print").click().then(() => {
                expect(win.print).to.be.called;
            })
        });
    });
});

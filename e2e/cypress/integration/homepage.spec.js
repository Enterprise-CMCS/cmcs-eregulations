describe("Homepage", () => {
    it("loads the homepage", () => {
        cy.visit("/");
        cy.contains("Medicaid & CHIP Regulations");
    });

    it("clicks on part 400 and loads the page", () => {
        cy.visit("/");
        cy.contains("400").click()

        cy.url().should('eq', Cypress.config().baseUrl + '/400/')
        cy.contains("This is the default landing view content to be displayed if no overrides exist.")
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.visit("/400/");
        cy.contains("Medicaid & CHIP Regulations").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
});

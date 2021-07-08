describe("Homepage", () => {
    it("loads the homepage", () => {
        cy.visit("/");
        cy.injectAxe()
        cy.contains("Medicaid & CHIP Regulations");
        cy.checkAccessibility();
    });

    it("clicks on part 430 and loads the page", () => {
        cy.visit("/");
        cy.contains("430").click()

        cy.url().should('eq', Cypress.config().baseUrl + '/42/430/')
        cy.contains("Grants to States for Medical Assistance Programs")
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.visit("/42/430/");
        cy.contains("Medicaid & CHIP Regulations").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
});

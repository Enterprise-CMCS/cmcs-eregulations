describe("Homepage", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] =
                Cypress.config().DEPLOYING_TO_PROD;
        });

    })

    it("loads the homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.injectAxe();
        cy.contains("Medicaid & CHIP eRegulations");
        cy.checkAccessibility();
    });

    it("clicks on part 430 and loads the page", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.contains("430").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/42/430/");
        cy.contains("Grants to States for Medical Assistance Programs");
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/430/");
        cy.contains("Medicaid & CHIP eRegulations").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
});

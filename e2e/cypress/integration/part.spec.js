describe("Part View", () => {
    it("loads part 433", () => {
        cy.visit("/433/");
        cy.contains("State Fiscal Administration").should("be.visible");
    });

    it("loads a section view", () => {
        cy.visit("/433/");
        cy.get(".toc-section-number").contains("433.50").click()

        cy.url().should("include", Cypress.config().baseUrl + "/433/50");
        cy.get("h1.section-title")
            .contains("433.50 Basis, scope, and applicability.")
            .should("be.visible");
    });

    it("loads a subpart view", () => {
        cy.visit("/433/");
        cy.contains("433.51").click()

        cy.contains("Subpart View").click();

        cy.url().should("include", "Subpart-B");
        cy.get("h1.section-title")
            .contains("General Administrative Requirements State Financial Participation")
            .should("be.visible");
    });

    it("loads a part view", () => {
        cy.visit("/433/");
        cy.contains("433.51").click()

        cy.get("a").contains("Part View").click();

        cy.url().should("include", "#433-51");
        cy.get("#433").contains("PART 433—STATE FISCAL ADMINISTRATION").should("be.visible");
        cy.get("#433-10").contains("433.10 Rates of FFP for program services.").should("be.visible");
        cy.get("#433-50").contains("433.50 Basis, scope, and applicability.").should("be.visible");
    });
});

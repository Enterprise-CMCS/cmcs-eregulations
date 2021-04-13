describe("Part View", () => {
    it("loads part 433", () => {
        cy.visit("/433/");
        cy.contains("State Fiscal Administration").should("be.visible");
    });

    it("section view redirects", () => {
        cy.visit("/433/");
        cy.get(".toc-section-number").contains("433.50").click()

        cy.url().should("include", Cypress.config().baseUrl + "/433/Subpart-B");
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
        cy.findByRole("link", { name: "§ 433.51 Public Funds as the State share of financial participation." }).click()

        cy.get("a").contains("Part View").click();

        // goes to first part of the appropriate subpart (this is odd)
        cy.url().should("include", "#433-50");
        cy.findByRole("heading", {level: 1, name: "§ 433.50 Basis, scope, and applicability."}).should("be.visible");
        cy.findByRole("heading", {level: 1, name: "§ 433.10 Rates of FFP for program services."}).should("be.visible");
    });
});

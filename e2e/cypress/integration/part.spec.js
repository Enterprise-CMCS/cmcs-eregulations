describe("Part View", () => {
    it("loads part 433", () => {
        cy.visit("/433/");
        cy.contains("State Fiscal Administration").should("be.visible");
    });

    it("section view redirects", () => {
        cy.visit("/433/");
        cy.get(".toc-section-number").contains("433.50").click()

        cy.url().should("include", Cypress.config().baseUrl + "/433/Subpart-B");
        cy.get("h2.section-title")
            .contains("433.50 Basis, scope, and applicability.")
            .should("be.visible");
    });

    it("loads a subpart view", () => {
        cy.visit("/433/");
        cy.contains("433.51").click()

        cy.url().should("include", "Subpart-B");
        cy.findByRole("heading", {level: 1, name: "Subpart B - General Administrative Requirements State Financial Participation"})
            .should("be.visible");
    });

    it("loads a part view", () => {
        cy.visit("/433/");
        cy.findByRole("link", { name: "433.1 Purpose." }).click()

        // goes to first part of the appropriate subpart (this is odd)
        cy.url().should("include", "#433-1");
        cy.findByRole("heading", {level: 1, name: "PART 433 - STATE FISCAL ADMINISTRATION"}).should("be.visible");
        cy.findByRole("heading", {level: 2, name: "§ 433.50 Basis, scope, and applicability."}).should("be.visible");
        cy.findByRole("heading", {level: 2, name: "§ 433.10 Rates of FFP for program services."}).should("be.visible");
    });

    it("loads a different version of a subpart", () => {
        cy.visit("/433/");
        cy.contains("433.10").click()

        cy.findByRole("button", {name: /View Past Versions/i}).should("be.visible");
        cy.findByRole("button", {name: /View Past Version/i}).click();
        cy.get(".view-and-compare").should("be.visible");
        
        cy.get("#view-options").select("2017-01-20");
        cy.url().should("include", "2017-01-20")

        cy.get(".close-button").click()
        cy.get(".view-and-compare").should("not.be.visible");
    });
});

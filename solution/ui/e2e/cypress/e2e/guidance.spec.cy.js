describe.skip("Guidance", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] =
                Cypress.env("DEPLOYING");
        });
        return
    })

    it("checks guidances on section 433.111", () => {
        cy.visit("/433/");
        cy.get(".toc-section-number").contains("433.111").click()

        cy.get("h1.section-title").contains("433.111 Definitions.");
        cy.get(".regs-meta").contains("Notices of Proposed Rulemaking").should("be.visible");
        cy.get(".regs-meta").contains("Final Rules").should("be.visible");
        cy.get(".regs-meta").contains("SMDL").should("be.visible");
        cy.get(".regs-meta").contains("State Medicaid Manual").should("be.visible");
    });

    it("goes the the next section after 433.111", () => {
        cy.visit("/433/");
        cy.get(".toc-section-number").contains("433.111").click()

        cy.get(".next-prev-label").contains("Next section").click();
        cy.url().should("include", Cypress.config().baseUrl + "/433/112");
    });

    it("goes the the previous section after 433.111", () => {
        cy.visit("/433/");
        cy.get(".toc-section-number").contains("433.111").click()

        cy.get(".next-prev-label").contains("Previous section").click();
        cy.url().should("include", Cypress.config().baseUrl + "/433/110");
    });
});

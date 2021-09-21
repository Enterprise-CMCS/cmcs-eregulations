describe("Part View", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        }).as("headers");
    });

    it("loads part 433", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");

        cy.injectAxe();
        cy.contains("Part 433 - State Fiscal Administration").should("be.visible");
        cy.checkAccessibility();
    });

    it("section view redirects", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.get(".toc-section-number").contains("433.50").click({ force: true });

        cy.url().should(
            "include",
            Cypress.config().baseUrl + "/42/433/Subpart-B"
        );
        cy.get("h2.section-title")
            .contains("433.50 Basis, scope, and applicability.")
            .should("be.visible");
    });

    it("loads a subpart view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.51").click({ force: true });

        cy.url().should("include", "Subpart-B");
        cy.get("#433-51-title").should("be.visible");
        cy.get("#subpart-resources-heading").contains("Subpart B Resources");
        cy.focused().then(($el) => {
            cy.get($el).should("have.id", "433-51");
        });
    });

    it("loads a part view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.findByRole("link", { name: "433.1 Purpose." }).click({
            force: true,
        });

        // goes to first part of the appropriate subpart (this is odd)
        cy.url().should("include", "#433-1");
        cy.get("#433-1-title").should("be.visible");
        cy.focused().then(($el) => {
            cy.get($el).should("have.id", "433-1");
        });
    });

    it("loads a different version of a subpart", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.10").click({ force: true });

        cy.findByRole("button", { name: /View Past Versions/i }).should(
            "be.visible"
        );
        cy.findByRole("button", { name: /View Past Versions/i }).click({
            force: true,
        });
        cy.get(".view-and-compare").should("be.visible");
        cy.get("#view-options").select("1/20/2017", { force: true });
        cy.url().should("include", "2017-01-20");

        cy.get("#close-link").click({ force: true });
        cy.get(".view-and-compare").should("not.be.visible");
    });
});

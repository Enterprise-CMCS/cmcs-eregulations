describe("Public Law 119-21 (OBBBBA)", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
        cy.intercept("**/v3/titles").as("titles");
    });

    it("loads the page", () => {
        cy.viewport("macbook-15");
        cy.visit("/pl119-21");
        cy.get("h1").contains("Public Law No. 119-21, July 4, 2025");
        cy.checkLinkRel();
        cy.injectAxe();
        cy.checkAccessibility();

        cy.get(".obbba__context")
            .then(($el) => {
                expect($el).to.have.css("font-style").and.eq("italic");
            });
    });

    it("jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.visit("/pl119-21");
        cy.wait("@titles");
        cy.jumpToRegulationPartSection({
            title: "42",
            part: "433",
            section: "40",
        });
    });

    it("goes to the State Medicaid Manual page using header link", () => {
        cy.viewport("macbook-15");
        cy.visit("/pl119-21");
        cy.clickHeaderLink({
            page: "manual",
            label: "State Medicaid Manual",
            screen: "wide",
        });
        cy.url().should("include", "/manual");
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.visit("/pl119-21");
        cy.goHome();
    });

    it("has a responsive toc", () => {
        cy.tocResponsiveChecks({
            page: "/pl119-21"
        });
    });
});

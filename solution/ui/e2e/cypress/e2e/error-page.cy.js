describe("Error page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("loads as a 404 page when server returns a 404 error", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.checkLinkRel();
        cy.injectAxe();
        cy.get(".error-code").invoke("text").should("include", "404");
        cy.get(".error-header")
            .invoke("text")
            .should(
                "include",
                "Sorry, the page you were looking for doesn't exist."
            );
        cy.checkAccessibility();
    });

    it("has a flash banner at the top with a link to a feedback survey", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.checkFlashBanner();
    });

    it("shows feedback form in modal when clicking feedback link in flash banner", () => {
        // feedback link is in banner
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.checkBlockingModal();
    });

    it("error-page - jumps to a regulation Part using the jump-to select", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.jumpToRegulationPart({ title: "45", part: "95" });
    });

    it("error-page - jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.jumpToRegulationPartSection({
            title: "42",
            part: "433",
            section: "40",
        });
    });

    it("error-page - goes to the Subjects page using header link", () => {
        cy.viewport("macbook-15");
        cy.visit("/about/");
        cy.clickHeaderLink({
            page: "subjects",
            label: "Find by Subject",
            screen: "wide",
        });
        cy.url().should("include", "/subjects");
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.goHome();
    });
});

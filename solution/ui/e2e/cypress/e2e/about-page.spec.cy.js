describe("About page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("should have rel='noopener noreferrer' on all external links", () => {
        cy.viewport("macbook-15");
        cy.visit("/about/");
        cy.checkLinkRel();
    });

    it("goes to the Subjects page using header link", () => {
        cy.viewport("macbook-15");
        cy.visit("/about/");
        cy.clickHeaderLink({
            page: "subjects",
            label: "Find by Subject",
            screen: "wide",
        });
        cy.url().should("include", "/subjects");
    });
});

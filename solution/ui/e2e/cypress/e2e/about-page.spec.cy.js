describe("About page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.env(["DEPLOYING"]).then(({ DEPLOYING }) => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = DEPLOYING;
            });
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
            label: "Research a Subject",
            screen: "wide",
        });
        cy.url().should("include", "/subjects");
    });

    it("goes to the State Medicaid Manual page using header link", () => {
        cy.viewport("macbook-15");
        cy.visit("/about/");
        cy.clickHeaderLink({
            page: "manual",
            label: "State Medicaid Manual",
            screen: "wide",
        });
        cy.url().should("include", "/manual");
    });
});

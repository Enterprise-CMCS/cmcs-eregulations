const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");
const readerUsername = Cypress.env("READER_USERNAME");
const readerPassword = Cypress.env("READER_PASSWORD");

describe("State Medicaid Manual page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("should have rel='noopener noreferrer' on all external links", () => {
        cy.viewport("macbook-15");
        cy.visit("/manual/");
        cy.checkLinkRel();
    });

    it("goes to the Subjects page using header link", () => {
        cy.viewport("macbook-15");
        cy.visit("/manual/");
        cy.clickHeaderLink({
            page: "subjects",
            label: "Research a Subject",
            screen: "wide",
        });
        cy.url().should("include", "/subjects");
    });

    it("shows the sign in Call to Action on landing page when not logged in", () => {
        cy.viewport("macbook-15");
        cy.visit("/manual", { timeout: 60000 });
        cy.get(".search__container .login-cta__div").contains(
            "To search within the manual, sign in or learn how to get account access.",
        );
        cy.get("span[data-testid=loginManual] a")
            .should("have.attr", "href")
            .and("include", "/login/?next=")
            .and("include", "/manual/");
        cy.get("a.access__anchor")
            .should("have.attr", "href")
            .and("include", "/get-account-access/");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/",
        });
        cy.visit("/manual");
        cy.get(".subj-landing__container .login-cta__div").should("not.exist");
    });
});

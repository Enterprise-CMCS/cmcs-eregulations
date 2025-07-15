const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

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

    // remove skip after addressing a11y issues
    it.skip("checks a11y for Get Account Access page", () => {
        cy.viewport("macbook-15");
        cy.visit("/manual", { timeout: 60000 });
        cy.checkLinkRel();
        cy.injectAxe();
        cy.checkAccessibility();
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

    it("should redirect to the Search page with the correct selected subject and filters when a search term is entered", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/manual");

        // Search for a term
        cy.get("input#main-content").type("mock", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        // Assert URL
        cy.url()
            .should("include", "/search")
            .and("include", "type=internal")
            .and("include", "intcategories=60");
    });
});

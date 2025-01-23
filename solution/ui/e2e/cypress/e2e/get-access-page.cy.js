const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

Cypress.Commands.add("checkHeaderLink", ({ shouldBeVisible = false }) => {
    const desiredState = shouldBeVisible ? "exist" : "not.exist";
    cy.get("a[data-testid='get-account-access-wide']").should(desiredState);
    cy.get("a[data-testid='get-account-access-narrow']").should(desiredState);
});

describe("Get Account Access page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("checks a11y for Get Account Access page", () => {
        cy.viewport("macbook-15");
        cy.visit("/get-account-access");
        cy.checkLinkRel();
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("goes to the Get Account Access page from homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("a[data-testid='get-account-access-narrow']").should(
            "not.be.visible",
        );
        cy.get("a[data-testid='get-account-access-wide']")
            .should("be.visible")
            .and("have.text", "Get Account Access")
            .and("have.attr", "class")
            .and("not.match", /active/);
        cy.get("a[data-testid='get-account-access-wide']").click();
        cy.url().should("include", "/get-account-access/");
        cy.get("a[data-testid='get-account-access-wide']")
            .should("be.visible")
            .and("have.text", "Get Account Access")
            .and("have.attr", "class")
            .and("match", /active/);
        cy.get("h1").contains("Get access to internal documents");
    });

    it("goes to the Get Account Access page from a SPA page like /subjects", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects");
        cy.get("a[data-testid='get-account-access-wide']").click();
        cy.url().should("include", "/get-account-access/");
    });

    it("should have a shorter header label on narrow screens", () => {
        cy.viewport("iphone-x");
        cy.visit("/");
        cy.get("a[data-testid='get-account-access-wide']").should(
            "not.be.visible",
        );
        cy.get("a[data-testid='get-account-access-narrow']")
            .should("be.visible")
            .and("have.text", "Get Access")
            .click();
        cy.url().should("include", "/get-account-access/");
        cy.get("h1").contains("Get access to internal documents");
    });

    it("should not show the header link when logged in", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.checkHeaderLink({ shouldBeVisible: true });

        cy.visit("/search");
        cy.checkHeaderLink({ shouldBeVisible: true });

        cy.visit("/subjects");
        cy.checkHeaderLink({ shouldBeVisible: true });

        cy.visit("/statutes");
        cy.checkHeaderLink({ shouldBeVisible: true });

        cy.eregsLogin({ username, password, landingPage: "/" });
        cy.checkHeaderLink({ shouldBeVisible: false });

        cy.visit("/search");
        cy.checkHeaderLink({ shouldBeVisible: false });

        cy.visit("/subjects");
        cy.checkHeaderLink({ shouldBeVisible: false });

        cy.visit("/statutes");
        cy.checkHeaderLink({ shouldBeVisible: false });
    });

    // if subjects page works, statutes and search do as well
    it("goes to the Subjects page using header link", () => {
        cy.viewport("macbook-15");
        cy.visit("/get-account-access/");
        cy.clickHeaderLink({
            page: "subjects",
            label: "Research a Subject",
            screen: "wide",
        });
        cy.url().should("include", "/subjects");
    });
});

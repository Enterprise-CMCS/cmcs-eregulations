const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

describe("Login and Logout Validation", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("checks a11y for sign in elements", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/" });
        cy.get("button[data-testid='user-account-button']").click({
            force: true,
        });
        cy.checkLinkRel();
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("should have a Sign In link at the top right corner of the header", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".header--sign-in a").should("be.visible");
        cy.get(".header--sign-in").should("not.have.class", "active");
        cy.get(".header--sign-in a").click();
        cy.url().should("include", "/?next=/");
        cy.get(".header--sign-in").should("have.class", "active");
        cy.get("h1").contains("Sign in with your CMS account");
        cy.get("main.login form")
            .should("be.visible")
            .and("contain", "Continue to CMS IDM");
    });

    it("should have an account info dropdown menu with Sign Out form on Django page when logged in", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/" });

        cy.get("button[data-testid='user-account-button']").should(
            "be.visible"
        );

        cy.get("button[data-testid='user-account-button']").should(
            "not.have.class",
            "user-account__button--expanded"
        );
        cy.get(".dropdown-menu__container.dropdown-menu--account").should(
            "not.exist"
        );
        cy.get("form#oidc_logout").should("not.exist");

        cy.get("button[data-testid='user-account-button']").click({
            force: true,
        });

        cy.get("button[data-testid='user-account-button']").should(
            "have.class",
            "user-account__button--expanded"
        );
        cy.get(".dropdown-menu__container.dropdown-menu--account").should(
            "be.visible"
        );
        cy.get("a[data-testid='manage-content-link']")
            .contains("Manage Content")
            .should("be.visible")
            .and("have.attr", "href")
            .and("include", "admin");
        cy.get("form#oidc_logout").should("be.visible");
        cy.get("form#oidc_logout").submit();
        cy.get(".dropdown-menu__container.dropdown-menu--account").should(
            "not.exist"
        );
        cy.get(".header--sign-in a").should("be.visible");
    });

    it("should have an account info dropdown menu with Sign Out button and hidden Sign Out form on Single Page App page when logged in", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/statutes" });

        cy.get("button[data-testid='user-account-button']").should(
            "be.visible"
        );

        cy.get("button[data-testid='user-account-button']").should(
            "not.have.class",
            "user-account__button--expanded"
        );
        cy.get(".dropdown-menu__container.dropdown-menu--account").should(
            "not.exist"
        );
        cy.get("form#oidc_logout").should("exist");
        cy.get("form#oidc_logout").should("not.be.visible");

        cy.get("button[data-testid='user-account-button']").click({
            force: true,
        });

        cy.get("button[data-testid='user-account-button']").should(
            "have.class",
            "user-account__button--expanded"
        );
        cy.get(".dropdown-menu__container.dropdown-menu--account").should(
            "be.visible"
        );
        cy.get("button[data-testid='vue-sign-out-button']").click({
            force: true,
        });
        cy.get(".dropdown-menu__container.dropdown-menu--account").should(
            "not.exist"
        );
        cy.get(".header--sign-in a").should("be.visible");
    });
});

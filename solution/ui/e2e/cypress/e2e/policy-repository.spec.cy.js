const TITLE_42 = 42;
const TITLE_45 = 45;

const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

const _beforeEach = () => {
    cy.intercept("/**", (req) => {
        req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
    });

    cy.intercept("**/v3/titles", [TITLE_42, TITLE_45]).as("titles");

    cy.intercept(`**/v3/title/${TITLE_42}/parts`, {
        fixture: "parts-42.json",
    }).as("parts42");

    cy.intercept(`**/v3/title/${TITLE_45}/parts`, {
        fixture: "parts-45.json",
    }).as("parts45");
};

describe("Policy Repository", () => {
    beforeEach(_beforeEach);

    it("shows the login screen when you visit /policy-repository/ without logging in", () => {
        cy.viewport("macbook-15");
        cy.visit("/policy-repository/");
        cy.url().should("include", "/admin/login");
    });

    it("show the policy repository page when logged in", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.url().should("include", "/policy-repository/");
        cy.get("#loginIndicator").should("be.visible");
    });

    it("should make a successful request to the file-manager/files endpoint", () => {
        cy.intercept("**/v3/file-manager/files").as("files");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.url().should("include", "/policy-repository/");
        cy.wait("@files").then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
        });
    });

    it("loads the correct subject when the URL is changed", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.url().should("include", "/policy-repository/");

        cy.get(`button[data-testid=add-subject-1]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=1");

        cy.get(`button[data-testid=add-subject-2]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=1,2");

        cy.get(`button[data-testid=add-subject-3]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=1,2,3");

        cy.go("back");
        cy.url().should("include", "/policy-repository?subjects=1,2");

        cy.get(`button[data-testid=remove-subject-2]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=1");
    });

    it("goes to another SPA page from the policy repository page", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.clickHeaderLink({ page: "Resources", screen: "wide" });
        cy.url().should("include", "/resources");
    });

    it("returns you to the admin login page when you log out", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.get("#logout").click();
        cy.get("#login-form").should("be.visible");
    });
});

describe("Policy Repository Search", () => {
    beforeEach(_beforeEach);

    it("shows the login screen when you visit /policy-repository/search without logging in", () => {
        cy.viewport("macbook-15");
        cy.visit("/policy-repository/search/");
        cy.url().should("include", "/admin/login");
    });

    it("show the policy repository search page when logged in", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/policy-repository/search" });
        cy.visit("/policy-repository/search");
        cy.url().should("include", "/policy-repository/search/");
        cy.get("#loginIndicator").should("be.visible");
    });

    it("should make a successful request to the file-manager/files endpoint", () => {
        cy.intercept("**/v3/file-manager/files**").as("queriedFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/policy-repository/search" });
        cy.visit("/policy-repository/search");
        cy.url().should("include", "/policy-repository/search/");
        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get(".search-field .v-input__icon--append button").click({
            force: true,
        });
        cy.url().should("include", "/policy-repository/search?q=test");
        cy.wait("@queriedFiles").then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
        });
    });
});

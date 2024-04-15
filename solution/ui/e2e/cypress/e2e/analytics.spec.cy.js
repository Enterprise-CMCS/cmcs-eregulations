const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");
const readerUsername = Cypress.env("READER_USERNAME");
const readerPassword = Cypress.env("READER_PASSWORD");

describe("Analytics", () => {
    it("does not render Google Analytics script tag if logged in as an admin", () => {
        cy.viewport("macbook-15");

        cy.visit("/");
        cy.get('head script[src*="googletagmanager"]').should("exist");

        cy.eregsLogin({ username: readerUsername, password: readerPassword, landingPage: "/" });
        cy.get('head script[src*="googletagmanager"]').should("exist");

        cy.get("#logout").click();

        cy.eregsLogin({ username, password, landingPage: "/" });
        cy.visit("/");
        cy.get('head script[src*="googletagmanager"]').should("not.exist");
    });

});

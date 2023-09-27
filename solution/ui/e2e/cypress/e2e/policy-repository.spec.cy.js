const TITLE_42 = 42;
const TITLE_45 = 45;

const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

describe("Policy Repository", () => {
    beforeEach(() => {
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
    });

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
        cy.intercept("**/v3/file-manager/files", (req) => {
            req.on("response", (res) => {
                expect(res.statusCode).to.eq(200);
            });
        });
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.url().should("include", "/policy-repository/");
    });


    it("returns you to the admin login page when you log out", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.get("#logout").click();
        cy.get("#login-form").should("be.visible");
    });
});

describe("Django admin login access control", () => {
    it("returns 404 when the Cypress token is missing", function () {
        if (Cypress.env("TEST_ENV") === "local") {
            this.skip();
        }

        cy.request({
            url: "/admin/login/",
            failOnStatusCode: false,
        }).its("status").should("eq", 404);
    });

    it("returns 404 when the Cypress token is incorrect", function () {
        if (Cypress.env("TEST_ENV") === "local") {
            this.skip();
        }

        cy.request({
            url: "/admin/login/",
            headers: {
                "X-eRegs-Cypress-Admin-Token": "incorrect-token",
            },
            failOnStatusCode: false,
        }).its("status").should("eq", 404);
    });
});

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

    it("shows the login page when the Cypress token is correct", function () {
        if (Cypress.env("TEST_ENV") === "local") {
            this.skip();
        }

        cy.request({
            url: "/admin/login/",
            headers: {
                "X-eRegs-Cypress-Admin-Token": Cypress.env("ADMIN_LOGIN_TOKEN"),
            },
        }).then((response) => {
            expect(response.status).to.equal(200);
            expect(response.body).to.include('id="id_username"');
        });
    });
});

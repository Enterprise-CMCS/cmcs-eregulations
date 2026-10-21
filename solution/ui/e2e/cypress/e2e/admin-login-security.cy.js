describe("Django admin login access control", () => {
    const expectedStatus = () =>
        Cypress.expose("ADMIN_LOGIN_TOKEN_REQUIRED") === "true" ? 404 : 200;

    it("enforces the configured policy when the Cypress token is missing", function () {
        if (Cypress.expose("TEST_ENV") === "local") {
            this.skip();
        }

        cy.request({
            url: "/admin/login/",
            failOnStatusCode: false,
        }).its("status").should("eq", expectedStatus());
    });

    it("enforces the configured policy when the Cypress token is incorrect", function () {
        if (Cypress.expose("TEST_ENV") === "local") {
            this.skip();
        }

        cy.request({
            url: "/admin/login/",
            headers: {
                "X-eRegs-Cypress-Admin-Token": "incorrect-token",
            },
            failOnStatusCode: false,
        }).its("status").should("eq", expectedStatus());
    });

    it("shows the login page when the Cypress token is correct", function () {
        if (Cypress.expose("TEST_ENV") === "local") {
            this.skip();
        }

        cy.env(["ADMIN_LOGIN_TOKEN"]).then(({ ADMIN_LOGIN_TOKEN }) => {
            cy.request({
                url: "/admin/login/",
                headers: {
                    "X-eRegs-Cypress-Admin-Token": ADMIN_LOGIN_TOKEN,
                },
            }).then((response) => {
                expect(response.status).to.equal(200);
                expect(response.body).to.include('id="id_username"');
            });
        });
    });
});

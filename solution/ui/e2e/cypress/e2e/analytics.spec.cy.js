describe("Analytics", () => {
    beforeEach(() => {
        cy.env(["DEPLOYING"]).then(({ DEPLOYING }) => {
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = DEPLOYING;
            }).as("headers");
        });
    });

    it("renders Google Analytics script tag if not logged in or logged in as a reader", () => {
        cy.viewport("macbook-15");

        cy.visit("/");
        cy.get('head script[src*="googletagmanager"]').should("exist");

        cy.env(["READER_USERNAME", "READER_PASSWORD"]).then(({ READER_USERNAME, READER_PASSWORD }) => {
            cy.eregsLogin({
                username: READER_USERNAME,
                password: READER_PASSWORD,
                landingPage: "/"
            });

            cy.visit("/");
            cy.get('head script[src*="googletagmanager"]').should("exist");

            cy.eregsLogout({ landingPage: "/" });
        })
    });

    it("does not render Google Analytics script tag if logged in as an admin", () => {
        cy.viewport("macbook-15");

        cy.visit("/");
        cy.get('head script[src*="googletagmanager"]').should("exist");

        cy.env(["TEST_USERNAME", "TEST_PASSWORD"]).then(({ TEST_USERNAME, TEST_PASSWORD }) => {
            cy.eregsLogin({
                username: TEST_USERNAME,
                password: TEST_PASSWORD,
                landingPage: "/"
            });

            cy.visit("/");
            cy.get('head script[src*="googletagmanager"]').should("not.exist");

            cy.eregsLogout({ landingPage: "/" });
        });
    });
});

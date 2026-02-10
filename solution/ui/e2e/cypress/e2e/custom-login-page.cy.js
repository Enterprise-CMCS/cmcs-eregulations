describe("custom login page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.env(["DEPLOYING"]).then(({ DEPLOYING }) => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = DEPLOYING;
            });
            cy.intercept("**/v3/titles").as("titles");
        });
    });

    it("custom-login-page - does not render an anchor for header Sign In link when on login page", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".header--sign-in a").should("exist");
        cy.get(".header--sign-in span.disabled").should("not.exist");

        cy.get(".header--sign-in a").click({ force: true });
        cy.get(".header--sign-in a").should("not.exist");
        cy.get(".header--sign-in span.disabled").should("exist");
    });

    it("custom-login-page - renders a custom login page", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.get(".login h1").should(
            "have.text",
            "Sign in with your CMS account",
        );
        cy.get(".login form")
            .should("exist")
            .and("have.text", "Continue to CMS IDM");
        cy.get("p[data-testid='new-user-msg']").should(
            "have.text",
            "New to signing in to eRegulations? Get account access.",
        );
        cy.get("a[data-testid='new-user-link']")
            .should("have.text", "Get account access")
            .and("have.attr", "href")
            .and("include", "/get-account-access");
        cy.get("a[data-testid='new-user-link']").click();
        cy.url().should("include", "/get-account-access");
    });

    it("custom-login-page - jumps to a regulation Part using the jump-to select", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.wait("@titles");
        cy.jumpToRegulationPart({ title: "45", part: "95" });
    });

    it("custom-login-page - jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.wait("@titles");
        cy.jumpToRegulationPartSection({
            title: "42",
            part: "433",
            section: "40",
        });
    });

    it("goes to the State Medicaid Manual page using header link", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.clickHeaderLink({
            page: "manual",
            label: "State Medicaid Manual",
            screen: "wide",
        });
        cy.url().should("include", "/manual");
    });


    it("custom-login-page - allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.goHome();
    });
});

describe("Error page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("loads as a 404 page when server returns a 404 error", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.injectAxe();
        cy.get(".error-code").invoke("text").should("include", "404");
        cy.get(".error-header")
            .invoke("text")
            .should(
                "include",
                "Sorry, the page you were looking for doesn't exist."
            );
        cy.checkAccessibility();
    });

    it("has a flash banner at the top with a link to a feedback survey", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.get("div.flash-banner").should("be.visible");

        cy.get("div.flash-banner .greeting")
            .invoke("text")
            // remove the space char
            .invoke("replace", /\u00a0/g, " ")
            .should("eq", "We welcome questions and suggestions — ");

        cy.get("div.flash-banner a").should("have.text", "give us feedback.");
    });

    it("shows feedback form in modal when clicking feedback link in flash banner", () => {
        // feedback link is in banner
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        // modal doesn't exist
        cy.get("div.blocking-modal-content").should("not.be.visible");
        // click link
        cy.get("div.flash-banner a")
            .should("have.text", "give us feedback.")
            .click({ force: true });
        // modal exists
        cy.get("div.blocking-modal-content").should("be.visible");
        // make sure background is right color etc
        cy.get("div.blocking-modal").should(
            "have.css",
            "background-color",
            "rgba(0, 0, 0, 0.8)"
        );
        // a11y
        cy.injectAxe();
        cy.checkAccessibility();
        // query iframe source to make sure it's google forms
        cy.get(".blocking-modal-content iframe#iframeEl")
            .should("have.attr", "src")
            .then((src) => {
                expect(src.includes("docs.google.com/forms")).to.be.true;
            });
        // click close
        cy.get("button.close-modal")
            .should("be.visible")
            .click({ force: true });
        // modal doesn't exist again
        cy.get("div.blocking-modal-content").should("not.be.visible");
    });

    it("jumps to a regulation Part using the jump-to select", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.get("#jumpToPart").select("433");
        cy.get("#jumpBtn").click({ force: true });

        cy.url().should("eq", Cypress.config().baseUrl + "/42/433/#433");
    });

    it("NEW -- jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.get("#jumpToPart").should("be.visible").select("433");
        cy.get("#jumpToSection").type("40");
        cy.get("#jumpBtn").click({ force: true });

        expect(
            Cypress.minimatch(
                cy.url(),
                "/42/433/Subpart-A/*/#433-40",
                {
                    matchBase: true,
                }
            )
        ).to.be.true;
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.request({ url: "/404", failOnStatusCode: false })
            .its("status")
            .should("equal", 404);
        cy.visit("/404", { failOnStatusCode: false });
        cy.contains("Medicaid & CHIP eRegulations").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
});

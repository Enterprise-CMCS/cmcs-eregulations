describe("Print Styles", () => {
    const destination = "/42/433/Subpart-A/2021-03-01/";
    const previousVersion = "/42/433/Subpart-A/2020-12-31/";

    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        }).as("headers");
        cy.intercept("**/v3/ecfr_parser_result/**").as("parserResult");

        cy.setCssMedia("screen");
    });

    it("has a print button in subpart view", () => {
        cy.viewport("macbook-15");
        cy.visit(destination);
        cy.window().then((win) => {
            cy.stub(win, "print");
            cy.get(".print-btn").contains("Print").click().then(() => {
                expect(win.print).to.be.called;
            })
        });
    });

    it("has proper print styles for latest version", () => {
        cy.viewport("macbook-15");
        cy.visit(destination);
        cy.wait("@parserResult");

        cy.get(".right-sidebar").should("be.visible");
        cy.get(".view-resources-link").should(($link) => {
            expect($link.first()).to.be.visible;
        });

        cy.get("footer .print-footer").should("have.css", "display", "none");

        cy.setCssMedia("print");

        cy.get(".left-sidebar").should("have.css", "display", "none");
        cy.get(".right-sidebar").should("have.css", "display", "none");
        cy.get("footer .site-footer").should("have.css", "display", "none");
        cy.get(".left-sidebar").should("have.css", "display", "none");

        cy.get(".view-resources-link").should(($link) => {
            expect($link.first()).to.not.be.visible;
        });

        cy.get("footer .print-footer").should("have.css", "display", "block");

        cy.get("header").should("have.css", "height", "48px");
        cy.get("header").should("have.css", "border-top-color", "rgb(2, 102, 102)");
        cy.get("header").should("have.css", "border-bottom-color", "rgb(2, 102, 102)");

        cy.get(".last-updated-date-print")
            .invoke('text')
            .should("match", /^\w{3} (\d{1}|\d{2}), \d{4}$/);
    })

    it("has proper print styles for a previous version", () => {
        cy.viewport("macbook-15");
        cy.visit(previousVersion);

        cy.get(".right-sidebar").should("be.visible");

        cy.get(".print-view-container").should("have.css", "display", "none");
        cy.get(".view-container").should("have.css", "display", "flex");

        cy.setCssMedia("print");

        cy.get(".print-view-container").should("have.css", "display", "block");
        cy.get(".view-container").should("have.css", "display", "none");
    })
});

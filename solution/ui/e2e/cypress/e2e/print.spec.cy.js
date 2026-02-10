describe("Print Styles", () => {
    const destination = "/42/433/Subpart-A/";
    const previousVersion = "/42/433/Subpart-A/2020-12-31/";

    beforeEach(() => {
        cy.env(["DEPLOYING"]).then(({ DEPLOYING }) => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = DEPLOYING;
            }).as("headers");

            cy.setCssMedia("screen");
        });
    });

    it("has proper print styles for latest version", () => {
        cy.viewport("macbook-15");
        cy.visit(destination);

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

        cy.get(".reg-history-link").should(($link) => {
            expect($link.first()).to.not.be.visible;
        });

        cy.get("footer .print-footer").should("have.css", "display", "block");

        cy.get("header").should("have.css", "height", "56px");
        cy.get("header").should("have.css", "border-top-color", "rgb(2, 102, 102)");
        cy.get("header").should("have.css", "border-bottom-color", "rgb(2, 102, 102)");
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

    it("has proper print styles for Public Law 119-21 (OBBBA)", () => {
        cy.viewport("macbook-15");
        cy.visit("/pl119-21");

        cy.setCssMedia("print");

        cy.get(".toc__nav").should("not.be.visible");
    })
});

const mainContentId = "#main-content";

describe("Homepage", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
        cy.intercept(
            "**/v3/resources/federal_register_docs?page=1&page_size=3&paginate=true",
            { fixture: "frdocs.json" }
        ).as("frdocs");
    });

    it("loads the homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/homepage_test/");
        cy.injectAxe();
        cy.contains("Medicaid & CHIP eRegulations");
        cy.checkAccessibility();
    });

    it("has a hidden Skip to main content link", () => {
        cy.viewport("macbook-15");
        cy.visit("/homepage_test/");
        cy.get(".ds-c-skip-nav").then(($el) => {
            const rect = $el[0].getBoundingClientRect();
            expect(rect.bottom).to.equal(-56); // hidden off-screen
        });
    });

    it("should have a div id on the page that matches the href of the skip to main content link", () => {
        cy.viewport("macbook-15");
        cy.visit("/homepage_test/");
        cy.get(".ds-c-skip-nav").should("have.attr", "href", mainContentId);
        cy.get(mainContentId).should("exist");
    });

    it("should have an open left nav on load on desktop", () => {
        cy.viewport("macbook-15");
        cy.visit("/homepage_test/");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
    });

    it("should have a closed left nav on load on tablet", () => {
        cy.viewport(800, 1024);
        cy.visit("/homepage_test/");
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
    });

    it("should have a closed left nav on mobile", () => {
        cy.viewport("iphone-x");
        cy.visit("/homepage_test/");
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
    });

    it("should responsively open and close the left nav if user does not click open/close button", () => {
        cy.viewport("macbook-15");
        cy.visit("/homepage_test/");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport(800, 1024);
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
        cy.viewport("macbook-15");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
    });

    it("should keep left nav open if user explicitly expands it, even if screen width changes", () => {
        cy.viewport(800, 1024);
        cy.visit("/homepage_test/");
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
        cy.get("button.nav-toggle__button").click({ force: true });
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport("macbook-15");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport(800, 1024);
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport("iphone-x");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
    });
});

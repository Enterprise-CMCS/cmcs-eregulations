export const tocResponsiveChecks = ({
    page = "/"
}) => {
    // it should have an open left nav on load on desktop
    cy.viewport("macbook-15");
    cy.visit(page);
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav open");

    // it should have a closed left nav on load on tablet"
    cy.viewport(800, 1024);
    cy.visit(page);
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav closed");

    // it should have a closed left nav on mobile
    cy.viewport("iphone-x");
    cy.visit(page);
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav closed");

    //should responsively open and close the left nav if user does not click open/close button
    cy.viewport("macbook-15");
    cy.visit(page);
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav open");
    cy.viewport(800, 1024);
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav closed");
    cy.viewport("macbook-15");
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav open");

    //should keep left nav open if user explicitly expands it, even if screen width changes
    cy.viewport(800, 1024);
    cy.visit(page);
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav closed");
    cy.get("button.nav-toggle__button").click({ force: true });
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav open");
    cy.viewport("macbook-15");
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav open");
    cy.viewport(800, 1024);
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav open");
    cy.viewport("iphone-x");
    cy.get("nav#leftNav").should("have.attr", "class", "toc__nav open");

};

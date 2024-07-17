export const checkPolicyDocs = ({ username, password, landingPage }) => {
    cy.intercept("**/v3/content-search/?q=mock**", {
        fixture: "policy-docs-search.json",
    }).as("queriedFiles");
    cy.intercept("**/v3/resources/public/categories**", {
        fixture: "categories.json",
    });
    cy.intercept("**/v3/resources/internal/categories**", {
        fixture: "categories-internal.json",
    });

    cy.viewport("macbook-15");
    cy.eregsLogin({
        username,
        password,
        landingPage,
    });
    cy.get("input#main-content")
        .should("be.visible")
        .type("mock", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

    cy.wait("@queriedFiles");

    // Internal doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .first()
        .should("include.text", " Internal")

    cy.get('[data-testid="results-item-categories"] i')
        .first()
        .should("have.class", "fa-key");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .first()
        .should("include.text", "Mock Category");

    // Public doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .eq(1)
        .should("include.text", " Public");

    cy.get('[data-testid="results-item-categories"] i')
        .eq(1)
        .should("have.class", "fa-users");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .eq(1)
        .should("include.text", "Subregulatory Test Guidance");

    cy.get('[data-testid="results-item-categories"] .subcategory-label')
        .eq(0)
        .should("include.text", "Mock Subcategory");

};

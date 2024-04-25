export const checkPolicyDocs = ({ username, password, landingPage }) => {
    cy.intercept("**/v3/content-search/?q=test**", {
        fixture: "policy-docs.json",
    }).as("queriedFiles");
    cy.viewport("macbook-15");
    cy.eregsLogin({
        username,
        password,
        landingPage,
    });
    cy.get("input#main-content")
        .should("be.visible")
        .type("test", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

    cy.wait("@queriedFiles");

    // Public doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .first()
        .should("include.text", " Public");

    cy.get('[data-testid="results-item-categories"] i')
        .first()
        .should("have.class", "fa-users");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .first()
        .should("include.text", "Subregulatory Guidance");

    cy.get('[data-testid="results-item-categories"] .subcategory-label')
        .first()
        .should("include.text", "CMCS Informational Bulletin (CIB)");

    // Internal doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .eq(1)
        .should("include.text", " Internal")

    cy.get('[data-testid="results-item-categories"] i')
        .eq(1)
        .should("have.class", "fa-key");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .eq(1)
        .should("include.text", "TestCat");

    cy.get('[data-testid="results-item-categories"] .subcategory-label')
        .eq(1)
        .should("include.text", "TestSubCat");

    //cy.get('[data-testid="division-label"]')
        //.first()
        //.should("include.text", "Uploaded by MG1 — MD1")
        //.and("have.attr", "title", "Mock Group 1 — Mock Division 1");
};

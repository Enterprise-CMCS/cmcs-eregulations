export const checkPolicyDocs = ({ username, password, landingPage }) => {
    cy.intercept("**/v3/title/42/parts", {
        fixture: "parts-last-updated.json",
    }).as("partsLastUpdated");
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
        .should("exist")
        .type("mock", { force: true });
    cy.get('[data-testid="search-form-submit"]').click({
        force: true,
    });

    cy.wait("@queriedFiles");

    //----- Internal doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .first()
        .should("include.text", " Internal");

    cy.get('[data-testid="results-item-categories"] i')
        .first()
        .should("have.class", "fa-key");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .first()
        .should("include.text", "TestCat");

    cy.get("[data-testid='results-item-context']")
        .first()
        .find('[data-testid="part-title"]')
        .should("not.exist");

    cy.get("[data-testid='results-item-context']")
        .first()
        .find('[data-testid="subpart-bar"]')
        .should("not.exist");

    cy.get("[data-testid='results-item-context']")
        .first()
        .find('[data-testid="subpart-title"]')
        .should("not.exist");

    // should have show related citations button 3541
    cy.get(".doc-list__document")
        .first()
        .find(".related-citations__btn--collapse")
        .should("include.text", "Show Related Citations");

    // related citations should be hidden by default
    cy.get(".doc-list__document")
        .first()
        .find(".collapse-content")
        .should("have.class", "invisible")
        .and("not.be.visible");

    // clicking the show related citations button should expand the related citations
    cy.get(".doc-list__document")
        .first()
        .find(".related-citations__btn--collapse")
        .click();

    cy.get(".doc-list__document")
        .first()
        .find(".related-citations__btn--collapse")
        .should("include.text", "Hide Related Citations");

    cy.get(".doc-list__document")
        .first()
        .find(".collapse-content")
        .should("not.have.class", "invisible")
        .and("be.visible")
        .find(".related-sections")
        .should("include.text", "Regulations: 42 CFR § 440.130")

    // clicking the hide related citations button should collapse the related citations
    cy.get(".doc-list__document")
        .first()
        .find(".related-citations__btn--collapse")
        .click();

    cy.get(".doc-list__document")
        .first()
        .find(".related-citations__btn--collapse")
        .should("include.text", "Show Related Citations");

    cy.get(".doc-list__document")
        .first()
        .find(".collapse-content")
        .should("have.class", "invisible")
        .and("not.be.visible");

    //----- Regulations Doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .eq(1)
        .should("include.text", "Public");

    cy.get('[data-testid="results-item-categories"] i')
        .eq(1)
        .should("have.class", "fa-users");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .eq(1)
        .should("include.text", "Regulations");

    cy.get("[data-testid='results-item-context']")
        .eq(1)
        .find('[data-testid="part-title"]')
        .should("include.text", "part 435—eligibility in the states, district of columbia, the northern mariana islands, and american samoa");

    cy.get("[data-testid='results-item-context']")
        .eq(1)
        .find('[data-testid="subpart-bar"]')
        .should("exist");

    cy.get("[data-testid='results-item-context']")
        .eq(1)
        .find('[data-testid="subpart-title"]')
        .should("include.text", "Subpart X—Fixture Data");

    // should NOT have show/hide related citations button
    cy.get(".doc-list__document")
        .eq(1)
        .find(".related-citations__btn--collapse")
        .should("not.exist");

    //----- Public doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .eq(2)
        .should("include.text", " Public");

    cy.get('[data-testid="results-item-context"]')
        .eq(2)
        .find(".recent-flag")
        .should("not.exist");

    cy.get('[data-testid="results-item-categories"] i')
        .eq(2)
        .should("have.class", "fa-users");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .eq(1)
        .should("include.text", "Related Regulations Fixture Item");

    cy.get('[data-testid="results-item-categories"] .subcategory-label')
        .eq(1)
        .should("include.text", "State Medicaid Director Letter (SMDL)");

    cy.get("[data-testid='results-item-context']")
        .eq(2)
        .find('[data-testid="part-title"]')
        .should("not.exist");

    cy.get("[data-testid='results-item-context']")
        .eq(2)
        .find('[data-testid="subpart-bar"]')
        .should("not.exist");

    cy.get("[data-testid='results-item-context']")
        .eq(2)
        .find('[data-testid="subpart-title"]')
        .should("not.exist");

    // should have show/hide related citations button 2057
    cy.get(".doc-list__document")
        .eq(2)
        .find(".related-citations__btn--collapse")
        .should("include.text", "Show Related Citations");

    // FR Doc
    cy.get('[data-testid="results-item-categories"] .doc-type__label')
        .eq(3)
        .should("include.text", " Public");

    cy.get('[data-testid="results-item-context"]')
        .eq(3)
        .find(".recent-flag")
        .should("include.text", "WD");

    cy.get('[data-testid="results-item-categories"] i')
        .eq(3)
        .should("have.class", "fa-users");

    cy.get('[data-testid="results-item-categories"] .category-label')
        .eq(2)
        .should("include.text", "Proposed and Final Rules");

    cy.get("[data-testid='results-item-context']")
        .eq(3)
        .find('[data-testid="part-title"]')
        .should("not.exist");

    cy.get("[data-testid='results-item-context']")
        .eq(3)
        .find('[data-testid="subpart-bar"]')
        .should("not.exist");

    cy.get("[data-testid='results-item-context']")
        .eq(3)
        .find('[data-testid="subpart-title"]')
        .should("not.exist");

    // should have show/hide related citations button 2302
    cy.get(".doc-list__document")
        .eq(3)
        .find(".related-citations__btn--collapse")
        .should("include.text", "Show Related Citations");
};

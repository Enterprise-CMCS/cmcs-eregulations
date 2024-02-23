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
    cy.get(".search-field .v-input__icon--append button").click({
        force: true,
    });

    // Public doc
    cy.get(".category-labels")
        .eq(0)
        .find(".doc-type__label")
        .should("include.text", " Public ")
        .find("i")
        .should("have.class", "fa-users");
    cy.get(".category-labels")
        .eq(0)
        .find(".category-label")
        .should("include.text", " Subregulatory Guidance ");
    cy.get(".category-labels")
        .eq(0)
        .find(".subcategory-label")
        .should("include.text", "CMCS Informational Bulletin (CIB)");

    // Internal doc
    cy.get(".category-labels")
        .eq(1)
        .find(".doc-type__label")
        .should("include.text", " Internal ")
        .find("i")
        .should("have.class", "fa-key");
    cy.get(".category-labels")
        .eq(1)
        .find(".category-label")
        .should("include.text", "TestCat");
    cy.get(".category-labels")
        .eq(1)
        .find(".subcategory-label")
        .should("include.text", "TestSubCat");
};

export const getPolicyDocs = ({
    username,
    password,
    query = "mock",
    fixture = "policy-docs.json",
}) => {
    cy.intercept(`**/v3/content-search/?q=${query}**`, {
        fixture,
    }).as("subjectFiles");
    cy.viewport("macbook-15");
    cy.eregsLogin({ username, password, landingPage: "/subjects/" });
    cy.visit(`/subjects/?q=${query}`);
    cy.injectAxe();
    cy.wait("@subjectFiles").then((interception) => {
        expect(interception.response.statusCode).to.eq(200);
    });
};

// Jump To
export const jumpToRegulationPart = ({ title, part }) => {
    cy.intercept(`**/v3/title/${title}/parts`).as("titleParts");
    cy.get("#jumpToTitle")
        .select(title, { force: true });
    cy.wait("@titleParts");
    cy.get("#jumpToTitle")
        .then(() => {
            cy.get("#jumpToPart").should("be.visible").select(part);
        });
    cy.get("#jumpBtn").click({ force: true });
    cy.url().should(
        "eq",
        Cypress.config().baseUrl + `/${title}/${part}/#${part}`
    );
};

export const jumpToRegulationPartSection = ({ title, part, section }) => {
    cy.intercept(`**/v3/title/${title}/parts`).as("titleParts");
    cy.get("#jumpToTitle").select(title);
    cy.wait("@titleParts");
    cy.get("#jumpToPart").should("be.visible").select(part);
    cy.get("#jumpToSection").type(section);
    cy.get("#jumpBtn").click({ force: true });

    cy.url().then((urlString) => {
        expect(
            Cypress.minimatch(
                urlString,
                Cypress.config().baseUrl +
                    `/${title}/${part}/Subpart-A/*/#${part}-${section}`,
                {
                    matchBase: false,
                }
            )
        ).to.be.true;
    });
};

// Jump To
export const jumpToRegulationPart = ({ title, part }) => {
    cy.get("#jumpToTitle")
        .select(title, { force: true });
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
    cy.get("#jumpToTitle").select(title);
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

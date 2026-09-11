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
        Cypress.config().baseUrl + `/${title}/${part}/full/#${part}`
    );
};

export const jumpToRegulationPartSection = ({ title, part, section }) => {
    cy.get("#jumpToTitle").select(title);
    cy.get("#jumpToPart").should("be.visible").select(part);
    cy.get("#jumpToSection").type(section);
    cy.get("#jumpBtn").click({ force: true });

    cy.url().then((urlString) => {
        const subpartMatch = Cypress.minimatch(
            urlString,
            Cypress.config().baseUrl +
                `/${title}/${part}/Subpart-*/#${part}-${section}`,
            {
                matchBase: false,
            }
        );
        const fullPartMatch =
            urlString ===
            Cypress.config().baseUrl + `/${title}/${part}/full/#${part}-${section}`;

        expect(subpartMatch || fullPartMatch).to.be.true;
    });
};

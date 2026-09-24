// Jump To
export const jumpToRegulationPart = ({ title, part }) => {
    cy.get("#jumpToTitle").select(title);
    cy.get("#jumpToPart").should("not.be.disabled");
    cy.get(`#jumpToPart option[value="${part}"]`).should("exist");
    cy.get("#jumpToPart").select(part);
    cy.get("#jumpToPart").should("have.value", part);
    cy.get("#jumpBtn").should("not.be.disabled").click();
    cy.url().should(
        "eq",
        Cypress.config().baseUrl + `/${title}/${part}/full/#${part}`
    );
};

export const jumpToRegulationPartSection = ({ title, part, section }) => {
    cy.get("#jumpToTitle").select(title);
    cy.get("#jumpToPart").should("not.be.disabled");
    cy.get(`#jumpToPart option[value="${part}"]`).should("exist");
    cy.get("#jumpToPart").select(part);
    cy.get("#jumpToPart").should("have.value", part);
    cy.get("#jumpToSection").type(section);
    cy.get("#jumpBtn").should("not.be.disabled").click();

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

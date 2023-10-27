export const checkLinkRel = () => {
    cy.log("Checking all links to sites");
    cy.get("a[target=_blank]:not([href*='mailto:'])").each((link) => {
        expect(link).to.have.attr("rel", "noopener noreferrer");
    });

};

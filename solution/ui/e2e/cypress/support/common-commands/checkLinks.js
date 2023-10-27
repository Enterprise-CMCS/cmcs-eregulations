export const checkLinkRel = () => {
    cy.log("Checking all links to sites");
    cy.get("a:not([href*='mailto:']).external").each((link) => {
        expect(link).to.have.attr("rel", "noopener noreferrer");
    });

};

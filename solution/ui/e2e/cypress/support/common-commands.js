// Flash Bannder/Blocking Modal
export const checkFlashBanner = () => {
    cy.get("div.flash-banner").should("be.visible");

    cy.get("div.flash-banner .greeting")
        .invoke("text")
        // remove the space char
        .invoke("replace", /\u00a0/g, " ")
        .should("eq", "We welcome questions and suggestions — ");

    cy.get("div.flash-banner a").should("have.text", "give us feedback.");
};

export const checkBlockingModal = () => {
    // modal doesn't exist
    cy.get("div.blocking-modal-content").should("not.be.visible");
    // click link
    cy.get("div.flash-banner a")
        .should("have.text", "give us feedback.")
        .click({ force: true });
    // modal exists
    cy.get("div.blocking-modal-content").should("be.visible");
    // make sure background is right color etc
    cy.get("div.blocking-modal").should(
        "have.css",
        "background-color",
        "rgba(0, 0, 0, 0.8)"
    );
    // a11y
    cy.injectAxe();
    cy.checkAccessibility();
    // query iframe source to make sure it's google forms
    cy.get(".blocking-modal-content iframe#iframeEl")
        .should("have.attr", "src")
        .then((src) => {
            expect(src.includes("docs.google.com/forms")).to.be.true;
        });
    // click close
    cy.get("button.close-modal").should("be.visible").click({ force: true });
    // modal doesn't exist again
    cy.get("div.blocking-modal-content").should("not.be.visible");
};

// Jump To
export const jumpToRegulationPart = ({ title, part }) => {
    cy.get("#jumpToTitle")
        .select(title, { force: true })
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

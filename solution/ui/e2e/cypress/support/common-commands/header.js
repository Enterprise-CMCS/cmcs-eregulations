// Flash Banner/Blocking Modal
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

export const goHome = () => {
    cy.contains("Medicaid & CHIP eRegulations").click();
    cy.url().should("eq", Cypress.config().baseUrl + "/");
};

export const clickHeaderLink = ({
    page = "statutes",
    label = "Statutes",
    screen = "wide",
}) => {
    const listLocation =
        screen === "wide"
            ? "header .header--links .links--container"
            : ".more--dropdown-menu";

    if (screen === "wide") {
        cy.get("button.more__button").should("not.be.visible");

        // not styled as selected
        cy.get(
            `${listLocation} > ul.links__list li a[data-testid=${page.toLowerCase()}]`
        )
            .should("be.visible")
            .should("have.attr", "class")
            .and("not.match", /active/);

        // click
        cy.get(
            `${listLocation} > ul.links__list li a[data-testid=${page.toLowerCase()}]`
        )
            .should("be.visible")
            .should("have.text", label)
            .click({ force: true });

        // styled as selected
        cy.get(
            `${listLocation} > ul.links__list li a[data-testid=${page.toLowerCase()}]`
        )
            .should("be.visible")
            .should("have.text", label)
            .should("have.attr", "class")
            .and("match", /active/);
    } else {
        cy.get(`${listLocation} > ul.links__list`).should("not.be.visible");

        cy.get(".more--dropdown-menu").should("not.be.visible");

        cy.get("button.more__button")
            .should("be.visible")
            .click({ force: true });

        cy.get(".more--dropdown-menu").should("be.visible");

        cy.get(
            `${listLocation} > ul.links__list li a[data-testid=${page.toLowerCase()}]`
        )
            .should("be.visible")
            .should("have.text", label)
            .click({ force: true });
    }
};

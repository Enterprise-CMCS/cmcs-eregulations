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
        cy.get(`${listLocation} ul.links__list`).should("not.exist");

        cy.get(".more--dropdown-menu").should("not.exist");

        cy.get("button.more__button")
            .should("be.visible")
            .click({ force: true });

        cy.get(".more--dropdown-menu").should("be.visible");

        // not styled as selected
        cy.get(
            `${listLocation} > ul.links__list li a[data-testid=${page.toLowerCase()}]`
        )
            .should("be.visible")
            .should("have.attr", "class")
            .and("not.match", /active/);

        cy.get(
            `${listLocation} ul.links__list li a[data-testid=${page.toLowerCase()}]`
        )
            .should("be.visible")
            .should("have.text", label)
            .click({ force: true });

        cy.get("button.more__button")
            .should("be.visible")
            .click({ force: true });

        // styled as selected
        cy.get(
            `${listLocation} > ul.links__list li a[data-testid=${page.toLowerCase()}]`
        )
            .should("be.visible")
            .should("have.text", label)
            .should("have.attr", "class")
            .and("match", /active/);
    }
};

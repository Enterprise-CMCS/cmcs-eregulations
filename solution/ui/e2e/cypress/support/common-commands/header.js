export const goHome = () => {
    cy.contains("Medicaid & CHIP eRegulations").click();
    cy.url().should("eq", Cypress.config().baseUrl + "/");
};

const expectedLabelsWide = ["OBBBA", "Social Security Act", "State Medicaid Manual", "Research a Subject"];

const checkLinkOrder = (listLocation, expectedLabels = expectedLabelsWide) => {
    cy.get(`${listLocation} > ul.links__list li a`).should(($links) => {
        const texts = [...$links].map((a) => a.textContent.trim());
        expect(texts).to.deep.equal(expectedLabels);
    });
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

        // links in correct order
        checkLinkOrder(listLocation);

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

        // links in correct order
        checkLinkOrder(listLocation);

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

describe("Resources page", () => {
    beforeEach(() => {
        indexedDB.deleteDatabase('eregs')
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] =
                Cypress.env("DEPLOYING");
        });
    })

    it("renders correctly", () => {
        cy.viewport("macbook-15");
        cy.visit("/resources");

        cy.get("h1").contains('Resources')
        cy.get("h3").contains('Filter Resources')
        // This is an anti pattern, sue me
        cy.wait(5000)
        cy.contains("100 results in Resources")
    });

    it("Selects parts and sections correctly", () => {
        cy.clearLocalStorage()
        cy.viewport("macbook-15");
        cy.visit("/resources");
        // Select Title 42 part 433
        cy.get('#select-parts > .v-btn__content').click();
        cy.get('[data-value="433"]').click();
        cy.url().should("include", "part=433");
        cy.url().should("include", "title=42");
        // Select subPart B
        cy.get('#select-subparts > .v-btn__content').click();
        cy.get('[data-value="433-B"]').click();
        cy.url().should("include", "part=433");
        cy.url().should("include", "title=42");
        cy.url().should("include", "subpart=433-B");
        // This might be brittle, but let's see how it goes
        cy.url().should("include", "section=433-50,433-51,433-52,433-53,433-54,433-55,433-56,433-57,433-58-433,433-66,433-67,433-68,433-70,433-72,433-74");
        // Just check on a random chip
        cy.get(".v-chip__content").contains("§ 433.53")
        // Select an additional section
        cy.get('#select-sections > .v-btn__content').click();
        cy.get('[data-value="433-11"]').click();
        cy.url().should("include", "433-11")
        cy.get(".v-chip__content").contains("§ 433.11")
        cy.go('back')
        cy.get(".v-chip__content").contains("§ 433.11").should('not.exist');
        // Just check on a random chip again
        cy.get(".v-chip__content").contains("§ 433.53")

    });

    it("Selects categories correctly", () => {
        cy.clearLocalStorage()
        cy.viewport("macbook-15");
        cy.visit("/resources");
        cy.get('#select-resource-categories > .v-btn__content').click();
        cy.get('[data-value="State Medicaid Director Letter (SMDL)"]').click();
        cy.url().should("include", "State%20Medicaid%20Director%20Letter%20%28SMDL%29")
        cy.get(".v-chip__content").contains("State Medicaid Director Letter (SMDL)")

    })
})
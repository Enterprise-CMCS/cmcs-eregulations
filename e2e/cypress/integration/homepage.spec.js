describe("Homepage", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
    });

    it("loads the homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.injectAxe();
        cy.contains("Medicaid & CHIP eRegulations");
        cy.checkAccessibility();
    });

    it("has a flash banner at the top indicating draft content", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("div.flash-banner").should("be.visible");
    });

    //it("hides the flash banner when scrolling down", () => {
        //cy.viewport("macbook-15");
        //cy.visit("/");
        //cy.scrollTo(0, 100);

        //cy.get("div.flash-banner").then(($el) => {
            //const rect = $el[0].getBoundingClientRect();

            //expect(rect.bottom).to.be.lessThan(1);
        //});
    //});

    //it("has the correct title and copy text", () => {

    //})

    it("jumps to a regulation Part using the jump-to select", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".jump-to-input select").select("433");
        cy.get(".jump-to > form").submit();

        cy.url().should("eq", Cypress.config().baseUrl + "/42/433/#433");
    });

    it("jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".jump-to-input select").should("be.visible").select("433");
        cy.get(".jump-to-input input.number-box").type("40");
        cy.get(".jump-to > form").submit();

        cy.url().should(
            "eq",
            Cypress.config().baseUrl + "/42/433/Subpart-A/2021-03-01/#433-40"
        );
    });

    it("clicks on part 430 and loads the page", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("#homepage-toc").contains("Part 430").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/42/430/");
        cy.contains("Grants to States for Medical Assistance Programs");
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/430/");
        cy.contains("Medicaid & CHIP eRegulations").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
});

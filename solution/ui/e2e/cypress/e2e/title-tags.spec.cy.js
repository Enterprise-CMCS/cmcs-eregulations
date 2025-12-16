describe("Updated HTML Title Tags", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept("**/v3/resources/subjects**", {
            fixture: "subjects.json",
        }).as("subjects");
    });

    it("Homepage title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.title().should("eq", "Medicaid & CHIP eRegulations");
    });

    it("About page title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/about/");
        cy.title().should("eq", "About This Tool | Medicaid & CHIP eRegulations");
    });

    it("Get Account Access page title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/get-account-access/");
        cy.title().should("eq", "Get Account Access | Medicaid & CHIP eRegulations");
    });

    it("Public Law No. 119-21 (OBBBBA) page title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/pl119-21/");
        cy.title().should(
            "eq",
            "Pub. L. 119-21 | Medicaid & CHIP eRegulations",
        );
    });

    it("Statutes page title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes/");
        cy.title().should(
            "eq",
            "Statute Reference | Medicaid & CHIP eRegulations",
        );
    });

    it("Subjects page without a selected subject", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");
        cy.title().should(
            "eq",
            "Find by Subject | Medicaid & CHIP eRegulations",
        );

        cy.get(".subjects__list button[data-testid=add-subject-63]")
            .should("have.text", "Managed Care")
            .click({ force: true });
        cy.title().should(
            "eq",
            "Managed Care | Find by Subject | Medicaid & CHIP eRegulations",
        );

        cy.go("back");
        cy.title().should(
            "eq",
            "Find by Subject | Medicaid & CHIP eRegulations",
        );
    });

    it("Subjects page with a selected subject already in URL", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");
        cy.title().should(
            "eq",
            "Find by Subject | Medicaid & CHIP eRegulations",
        );

        cy.visit("/subjects/?subjects=1");
        cy.title().should(
            "eq",
            "Cures Act | Find by Subject | Medicaid & CHIP eRegulations",
        );

        cy.visit("/subjects/?subjects=18");
        cy.title().should(
            "eq",
            "Collateral Contacts | Find by Subject | Medicaid & CHIP eRegulations",
        );
    });
});

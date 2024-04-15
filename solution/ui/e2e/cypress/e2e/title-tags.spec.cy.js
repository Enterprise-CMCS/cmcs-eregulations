describe("Updated HTML Title Tags", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("**/v3/file-manager/subjects", {
            fixture: "subjects.json",
        }).as("subjects");
    });

    it("Homepage title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.title().should("eq", "Medicaid & CHIP eRegulations");
    });

    it("Statutes page title tags", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes/");
        cy.title().should(
            "eq",
            "Statute Reference | Medicaid & CHIP eRegulations"
        );
    });

    it("Subjects page without a selected subject", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");
        cy.title().should(
            "eq",
            "Find by Subject | Medicaid & CHIP eRegulations"
        );

        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", " Managed Care ")
            .click({ force: true });
        cy.title().should(
            "eq",
            "Managed Care | Find by Subject | Medicaid & CHIP eRegulations"
        );

        cy.go("back");
        cy.title().should(
            "eq",
            "Find by Subject | Medicaid & CHIP eRegulations"
        );
    });

    it("Subjects page with a selected subject already in URL", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");
        cy.title().should(
            "eq",
            "Find by Subject | Medicaid & CHIP eRegulations"
        );
    });
});

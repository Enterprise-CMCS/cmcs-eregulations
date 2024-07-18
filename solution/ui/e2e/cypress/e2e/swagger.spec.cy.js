describe("Swagger View", () => {

    it.skip("loads the swagger page", () => {
        cy.viewport("macbook-15");
        cy.visit("/api/swagger/");
        cy.contains("CMCS eRegulations API").should(
            "be.visible"
        );
        cy.contains("/api/schema/").should(
            "be.visible"
        );
        cy.contains("Schemas").should(
            "be.visible"
        );
    });
})
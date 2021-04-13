describe("Search flow", () => {
    it("shows up on the homepage", () => {
        cy.visit("/");
        cy.findByPlaceholderText("Search Regulations")
            .should("be.visible")
            .type("State");
        cy.get(".search-header .search-box").submit();

        cy.url().should("include", "/search/?q=State");
    });

    it("displays results of the search", () => {
        cy.visit("/search/?q=State");
        cy.findByText("60 results, displayed by relevance").should("be.visible");
        cy.findByRole("link", {name: "§ 433.153 Incentive payments to States and political subdivisions."}).should("be.visible").and('have.attr', 'href');
        cy.findByRole("link", {name: "§ 433.153 Incentive payments to States and political subdivisions."}).click();
        cy.url().should("include", "/433/Subpart-D/2020-28567/#433-153");
    });

    it("links to a search in the eCFR", () => {
        cy.visit("/search/?q=State");
        cy.findByRole("link", {name: "State in Beta eCFR", exact: false}).should("have.attr", "href", "https://ecfr.federalregister.gov/search?search%5Bdate%5D=current&search%5Bhierarchy%5D%5Btitle%5D=42&search%5Bquery%5D=State&view=standard");
    });

    it("should have a working searchbox", () => {
        cy.visit("/search/?q=State");
        cy.findByPlaceholderText("State")
            .should("be.visible")
            .type("test");
        cy.get("main .search-box").submit();
        cy.url().should("include", "/search/?q=test");
    });

    it("should be able to clear the searchbox", () => {
        cy.visit("/search/?q=State");

        cy.findByPlaceholderText("State")
            .should("be.visible")
            .type("test");

        cy.findByDisplayValue("test")
            .should("be.visible")
            .should("have.value", "test");

        cy.get(".search-reset").click();
        
        cy.findByPlaceholderText("State")
            .should("have.value", "");
    });
});

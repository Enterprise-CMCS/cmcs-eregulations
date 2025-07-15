describe("Statute Table", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept(`**/v3/statutes**`, {
            fixture: "statutes.json",
        }).as("statutes");

        cy.intercept(`**/v3/acts`, {
            fixture: "acts.json",
        }).as("acts");
    });

    it("goes to statutes page from homepage and has SSA Title 19 selected by default", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.clickHeaderLink({
            page: "statutes",
            label: "Social Security Act",
            screen: "wide",
        });
        cy.url().should("include", "/statutes/");

        cy.get("h1").contains("Look Up Statute Text");

        cy.get(".table__caption")
            .contains(
                "This table shows sections of 42 U.S.C. Chapter 7 (Social Security) enacted by the Social Security Act. Learn about these sources: US Code House.gov, Statute Compilation, US Code Annual, SSA.gov Compilation."
            );

        cy.checkLinkRel();

        cy.get("a[data-testid=ssa-XIX-19]").should(
            "have.class",
            "titles-list__link--active"
        );
        cy.get("a[data-testid=ssa-XI-11]").should(
            "not.have.class",
            "titles-list__link--active"
        );
    });

    it("displays as a table at widths 1024px wide and greater", () => {
        cy.viewport(1024, 768);
        cy.visit("/statutes");
        cy.get("#statuteTable").should("be.visible");
        cy.get("#statuteList").should("not.exist");
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("displays as a list at widths narrower than 1024px", () => {
        cy.viewport(1023, 1000);
        cy.visit("/statutes");
        cy.get("#statuteTable").should("not.exist");
        cy.get("#statuteList").should("be.visible");
        cy.injectAxe();
        cy.checkAccessibility();
    });

    it("statutes link nested in a dropdown menu on mobile screen widths", () => {
        cy.viewport("iphone-x");
        cy.visit("/");
        cy.clickHeaderLink({
            page: "statutes",
            label: "Social Security Act",
            screen: "narrow",
        });
        cy.url().should("include", "/statutes/");
    });

    it("loads the correct act and title when the URL is changed", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes");

        cy.clickStatuteLink({ act: "ssa", titleRoman: "XXI", title: "21" });
        cy.url().should("include", "/statutes?act=ssa&title=21");

        cy.clickStatuteLink({ act: "ssa", titleRoman: "XI", title: "11" });
        cy.url().should("include", "/statutes?act=ssa&title=11");
    });

    it("goes to another SPA page from the statutes page", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes");
        cy.clickHeaderLink({
            page: "subjects",
            label: "Research a Subject",
            screen: "wide",
        });
        cy.url().should("include", "/subjects");
    });
});

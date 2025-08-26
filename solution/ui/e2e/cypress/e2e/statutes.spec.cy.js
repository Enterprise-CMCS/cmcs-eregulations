describe("Statute Table", () => {
    beforeEach(() => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });

        cy.intercept(`**/v3/statutes**`, {
            fixture: "statutes.json",
        }).as("statutes");

        cy.intercept(`**/v3/statute-link/?pattern=1903`, {
            fixture: "statute-link.json",
        }).as("statute-link");

        cy.intercept(`**/v3/statute-link/?pattern=asdf`, {
            fixture: "statute-link-not-found.json",
            statusCode: 404,
        }).as("statute-link-not-found");

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

        cy.get("h1").contains("Social Security Act");

        cy.get("h2")
            .eq(0)
            .contains("Look up Statute Text");

        cy.get("h2")
            .eq(1)
            .contains("Table of Contents");

        cy.get(".p__description")
            .contains(
                "List of sections of 42 U.S.C. Chapter 7 enacted by the Social Security Act."
            );

        cy.checkLinkRel();

        cy.get("button[data-testid=ssa-XIX-19]").should(
            "have.class",
            "v-tab-item--selected"
        );
        cy.get("button[data-testid=ssa-XI-11]").should(
            "not.have.class",
            "v-tab-item--selected"
        );
    });

    it("looks up a statute citation as expected", () => {
        cy.viewport("macbook-15");
        cy.visit("/statutes");

        cy.get("form label.statute-citation-lookup__form--label")
            .contains("Social Security Act §");

        cy.get(".more-info__container")
            .should("not.exist");

        cy.get("button[data-testid=clear-citation-input]")
            .should("not.be.visible");

        cy.get("input#citationInput")
            .should("exist")
            .and("have.value", "")
            .and("have.attr", "placeholder", "1903(a)(3)(A)(i)")
            .type("1903", { force: true });

        cy.get("button[data-testid=clear-citation-input]")
            .should("be.visible");

        cy.get("button#citationSubmit")
            .should("exist")
            .contains("Get Citation Link")
            .click({ force: true });

        cy.wait("@statute-link");

        cy.get(".more-info__container").within(() => {
            cy.get("h3").contains("Citation Link");
            cy.get(".more-info__row")
                .eq(0)
                .within(() => {
                    cy.get("button.action-btn")
                        .should(($el) => {
                            expect($el.text().trim()).to.equal(
                                "copy link",
                            );
                        });
                    cy.get("a")
                        .should("have.attr", "href", "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim")
                        .and("have.attr", "target", "_blank")
                        .and("have.attr", "rel", "noopener noreferrer")
                        .and("have.attr", "class", "external")
                        .and("contain", "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1396b&num=0&edition=prelim")
                });
        });

        cy.get("button[data-testid=clear-citation-input]")
            .click({ force: true });

        cy.get("button[data-testid=clear-citation-input]")
            .should("not.be.visible");

        cy.get(".more-info__container")
            .should("not.exist");

        cy.get("input#citationInput")
            .should("exist")
            .and("have.value", "")
            .type("asdf", { force: true });

        cy.get("button#citationSubmit")
            .should("exist")
            .contains("Get Citation Link")
            .click({ force: true });

        cy.get(".more-info__container").within(() => {
            cy.get("h3").contains("Citation Link");
            cy.get(".more-info__row")
                .eq(0)
                .within(() => {
                    cy.get(".row__content")
                        .and("contain", "No citation link found for the provided pattern.");
                });
        });

        cy.get(".more-info__container").within(() => {
            cy.get("h3").contains("Citation Link");
            cy.get(".more-info__row")
                .eq(1)
                .should("not.exist");
        });
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

        cy.clickStatuteTab({ act: "ssa", titleRoman: "XXI", title: "21" });
        cy.url().should("include", "/statutes?act=ssa&title=21");

        cy.clickStatuteTab({ act: "ssa", titleRoman: "XI", title: "11" });
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

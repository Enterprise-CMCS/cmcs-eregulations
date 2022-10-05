describe("Resources page", () => {
    describe("Loading and Empty States", () => {
        beforeEach(() => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
            });
        });

        it("render correctly", () => {
            cy.intercept("**/resources/?**", {
                fixture: "no-resources-results.json",
                delayMs: 1000,
            }).as("resources");
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.injectAxe();
            cy.get(".results-count > span").should(
                "contain.text",
                "Loading..."
            );
            cy.get("h1").contains("Resources");
            cy.get("h3").contains("Filter Resources");
            cy.get(".results-count > span").should(
                "contain.text",
                "0 results in Resources"
            );
            cy.get(".empty-state-container").should("exist");
            cy.checkAccessibility();
        });
    });

    describe("Mock Results", () => {
        beforeEach(() => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
            });
            cy.intercept("**/resources/?locations=42**page=1**", {
                fixture: "resources.json",
            }).as("resources");
            cy.intercept("**/resources/?locations=42**page=2**", {
                fixture: "resources-page-2.json",
            }).as("resources2");
        });

        it("renders correctly", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.injectAxe();
            cy.get("h1").contains("Resources");
            cy.get("h3").contains("Filter Resources");
            cy.wait("@resources").then((interception) => {
                const count = interception.response.body.count;
                cy.get(".results-count > span").contains(
                    `1 - 100 of ${count} results in Resources`
                );
                cy.get(".empty-state-container").should("not.exist");
                cy.checkAccessibility();
            });
        });

        it("Selects parts correctly", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.injectAxe();
            cy.get("h1").contains("Resources");
            // Select Title 42 part 400
            cy.get("button#select-parts").should("not.have.attr", "disabled");
            cy.get("button#select-parts").click({ force: true });
            cy.checkAccessibility();
            cy.get('[data-value="400"]').click();
            cy.url().should("include", "part=400");
            cy.url().should("include", "title=42");
        });

        it("Chips follow the URL values correctly", () => {
            const sectionString =
                "433-50,433-51,433-52,433-53,433-54,433-55,433-56,433-57,433-58-433,433-66,433-67,433-68,433-70,433-72,433-74";
            cy.viewport("macbook-15");
            cy.visit(
                `/resources?title=42&part=433&subpart=433-B&section=${sectionString}`
            );
            cy.injectAxe();
            sectionString.split(",").forEach((ss) => {
                cy.get(".v-chip__content").contains(
                    `§ ${ss.replace("-", ".")}`
                );
            });
            cy.checkAccessibility();
            // Select an additional section
            cy.visit(
                "/resources?title=42&part=433&subpart=433-B&section=433-11"
            );
            cy.url().should("include", "433-11");
            cy.get(".v-chip__content").contains("§ 433.11");
            cy.go("back");
            cy.get(".v-chip__content").contains("§ 433.11").should("not.exist");
            // Just check on a random chip again
            cy.get(".v-chip__content").contains("§ 433.53");
        });

        it("Goes to the second page of results when clicking the Next button", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.injectAxe();
            cy.get("h1").contains("Resources");
            cy.get("h3").contains("Filter Resources");
            cy.wait("@resources");
            cy.get(".current-page.selected").contains("1");
            cy.get(".pagination-control.right-control")
                .contains("Next")
                .click({ force: true });
            cy.wait("@resources2").then((interception) => {
                const count = interception.response.body.count;
                cy.url().should("include", "page=2");
                cy.get(".results-count > span").contains(
                    `101 - 200 of ${count} results in Resources`
                );
                cy.get(".current-page.selected").contains("2");
            });
        });
        // it("Goes to the second page of results when clicking on page 2")
        // it("Goes to the second page of results on load when page=2 in the URL")

        it.skip("Selects categories correctly", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.get("#select-resource-categories > .v-btn__content").click();
            cy.get(
                '[data-value="State Medicaid Director Letter (SMDL)"]'
            ).click();
            cy.url().should(
                "include",
                "State%20Medicaid%20Director%20Letter%20%28SMDL%29"
            );
            cy.get(".v-chip__content").contains(
                "State Medicaid Director Letter (SMDL)"
            );
        });
    });
});

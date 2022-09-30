describe("Resources page", () => {
    describe("Empty State", () => {
        it("renders correctly", () => {
            cy.intercept("**/resources/**", {
                fixture: "no-resources-results.json",
                delayMs: 1000,
            }).as("resources");
            cy.clearIndexedDB();
            cy.visit("/resources");
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
        });
    });

    describe("Mock Results", () => {
        beforeEach(() => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
            });
            cy.intercept("**/resources/?locations=42**", {
                fixture: "resources.json",
            }).as("resources");
            cy.intercept("*v2/title/42/existing", {
                fixture: "42-existing.json",
            }).as("existing");
            cy.intercept("*v3/toc", { fixture: "toc.json" }).as("toc");
        });

        it("renders correctly", () => {
            // THis is to prove the concept of fetching the resources not from our API, but from a cypress fixture
            cy.intercept("**/resources/?locations=42**", {
                fixture: "resources.json",
            }).as("resources");
            cy.intercept("*v2/title/42/existing", {
                fixture: "42-existing.json",
            }).as("existing");
            cy.intercept("*v3/toc", { fixture: "toc.json" }).as("toc");
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.get("h1").contains("Resources");
            cy.get("h3").contains("Filter Resources");
            cy.get(".results-count > span").contains(
                "1 - 100 of 2101 results in Resources"
            );
        });

        it.skip("Selects parts correctly", () => {
            cy.clearLocalStorage();
            cy.viewport("macbook-15");
            cy.visit("/resources");
            // Select Title 42 part 433
            cy.get("#select-parts > .v-btn__content").click();
            cy.get('[data-value="433"]').click();
            cy.url().should("include", "part=433");
            cy.url().should("include", "title=42");
        });

        it.skip("Chips follow the URL values correctly", () => {
            const sectionString =
                "433-50,433-51,433-52,433-53,433-54,433-55,433-56,433-57,433-58-433,433-66,433-67,433-68,433-70,433-72,433-74";
            cy.viewport("macbook-15");
            cy.visit(
                `/resources?title=42&part=433&subpart=433-B&section=${sectionString}`
            );
            sectionString.split(",").forEach((ss) => {
                cy.get(".v-chip__content").contains(
                    `§ ${ss.replace("-", ".")}`
                );
            });
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

describe("Resources page", () => {
    describe("Header Link", () => {
        beforeEach(() => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
            });
        });

        it("goes to resources page from homepage", () => {
            cy.viewport("macbook-15");
            cy.visit("/");
            cy.get("button.more__button")
                .should("not.be.visible");

            cy.get("header .header--links .links--container > ul.links__list li:first-child a")
                .should("be.visible")
                .should("have.text", "Resources")
                .click({ force: true });

            cy.url().should("include", "/resources");
        });

        it("is styled correctly when at Resources page", () => {
            cy.viewport("macbook-15");
            cy.visit("/");
            cy.get("header .header--links .links--container > ul.links__list li:first-child a")
                .should("be.visible")
                .should("have.attr", "class")
                .and("not.match", /active/);

            cy.get("header .header--links .links--container > ul.links__list li:first-child a")
                .click({ force: true });

            cy.get("header .header--links .links--container > ul.links__list li:first-child a")
                .should("be.visible")
                .should("have.text", "Resources")
                .should("have.attr", "class")
                .and("match", /active/);
            ;
        });

        it("is nested in a dropdown menu on narrow screen widths", () => {
            cy.viewport("iphone-x");
            cy.visit("/");
            cy.get("header .header--links .links--container > ul.links__list")
                .should("not.be.visible")

            cy.get(".more--dropdown-menu")
                .should("not.be.visible");

            cy.get("button.more__button")
                .should("be.visible")
                .click({ force: true });

            cy.get(".more--dropdown-menu")
                .should("be.visible");

            cy.get(".more--dropdown-menu > ul.links__list li:first-child a")
                .should("be.visible")
                .should("have.text", "Resources")
                .click({ force: true });

            cy.url().should("include", "/resources");

        });

    });

    describe("Loading and Empty States", () => {
        beforeEach(() => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
            });
            cy.intercept("**/v3/resources/?&**page=1**", {
                fixture: "no-resources-results.json",
                delayMs: 1000,
            }).as("resources");
        });

        it("load properly", () => {
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
            cy.intercept("**/v3/resources/?&**page=1**", {
                fixture: "resources.json",
            }).as("resources");
            cy.intercept("**/v3/resources/?&**page=2**", {
                fixture: "resources-page-2.json",
            }).as("resources2");
        });

        it("does not filter locations on the search", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.wait("@resources").then( (interception) => {
              expect(interception.request.url).to.not.contain( 'location=')
            });
        })

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
            cy.get('[data-value="400"]').click({ force: true });
            cy.url().should("include", "part=400");
            cy.url().should("include", "title=42");
            cy.get("button#select-parts").click({ force: true });
            cy.checkAccessibility();
        });

        it("Sorts results correctly", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.injectAxe();
            cy.get("h1").contains("Resources");
            cy.get("button#sortButton").should("not.have.attr", "disabled");
            cy.get("button#sortButton").click({ force: true });
            cy.get('[data-value="newest"]').click({ force: true });
            cy.url().should("include", "sort=newest");
            cy.get("button#sortButton").click({ force: true });
            cy.checkAccessibility();
        });

        it("Selects categories correctly", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.injectAxe();
            cy.get("button#select-resource-categories").should("not.have.attr", "disabled");
            cy.get("#select-resource-categories").click({
                force: true,
            });
            cy.get(
                '[data-value="State Medicaid Director Letter (SMDL)"]'
            ).click({ force: true });
            cy.url().should(
                "include",
                "State%20Medicaid%20Director%20Letter%20%28SMDL%29"
            );
            cy.get(".v-chip__content").contains(
                "State Medicaid Director Letter (SMDL)"
            );
            cy.get("#select-resource-categories").click({
                force: true,
            });
            cy.checkAccessibility();
        });

        it("Chips follow the URL values correctly", () => {
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
            cy.injectAxe();
            cy.get(".v-chip__content").contains("§ 433.11").should("not.exist");
            // Just check on a random chip again
            cy.get(".v-chip__content").contains("§ 433.53");
            cy.checkAccessibility();
        });

        it("Goes to the second page of results when clicking the Next button", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.get("h1").contains("Resources");
            cy.get("h3").contains("Filter Resources");
            cy.wait("@resources");
            cy.get(".current-page.selected").contains("1");
            cy.get(".pagination-control.left-control > .back-btn").should(
                "have.class",
                "disabled"
            );
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

        it("Goes to the second page of results when clicking on page 2", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources");
            cy.get("h1").contains("Resources");
            cy.get("h3").contains("Filter Resources");
            cy.wait("@resources");
            cy.get(".current-page.selected").contains("1");
            cy.get(".page-number-li.unselected")
                .contains("2")
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

        it("Goes to the second page of results on load when page=2 in the URL", () => {
            cy.viewport("macbook-15");
            cy.visit("/resources/?page=2");
            cy.get("h1").contains("Resources");
            cy.get("h3").contains("Filter Resources");
            cy.wait("@resources2").then((interception) => {
                const count = interception.response.body.count;
                cy.get(".results-count > span").contains(
                    `101 - 200 of ${count} results in Resources`
                );
                cy.get(".current-page.selected").contains("2");
            });
        });
    });
});

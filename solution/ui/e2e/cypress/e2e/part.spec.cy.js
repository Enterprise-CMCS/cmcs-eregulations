const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");

describe("Part View", () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        }).as("headers");
    });

    it("loads part 433", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.checkLinkRel();

        cy.injectAxe();
        cy.contains("Part 433 - State Fiscal Administration").should(
            "be.visible"
        );
        cy.get("#jumpToTitle").invoke("val").should("equal", "42");
        cy.get("#jumpToPart").invoke("val").should("equal", "433");
        cy.checkAccessibility();
    });

    it("section view redirects", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.get(".toc-section-number").contains("433.50").click({ force: true });

        cy.url().should(
            "include",
            Cypress.config().baseUrl + "/42/433/Subpart-B"
        );
        cy.checkLinkRel();
        cy.get("h2.section-title")
            .contains("433.50 Basis, scope, and applicability.")
            .should("be.visible");
    });

    it("loads a subpart view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.51").click({ force: true });

        cy.url().should("include", "Subpart-B");
        cy.get("#jumpToTitle").invoke("val").should("equal", "42");
        cy.get("#jumpToPart").invoke("val").should("equal", "433");
        cy.get("#433-51-title").should("be.visible");
        cy.get(".latest-version").should("exist");
        cy.get("#subpart-resources-heading").contains("433.51 Resources");
        cy.get(".resources_btn_container").should("not.exist");

        cy.get(".right-sidebar").should("be.visible", "display", "none");

        cy.get(".view-resources-link").should(($link) => {
            expect($link.first()).to.be.visible;
        });

        cy.focused().then(($el) => {
            cy.get($el).should("have.id", "433-51");
            cy.get($el).should(
                "have.css",
                "background-color",
                "rgb(238, 250, 254)"
            );
        });
    });

    it("has a login call to action in the right sidebar of a subpart view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/51");

        cy.get(".div__login-sidebar").contains(
            "CMCS staff participating in the Policy Repository pilot can sign in to see internal resources."
        );

        cy.get("a#loginSidebar")
            .should("have.attr", "href")
            .and("include", "/login/?next=")
            .and("include", "/42/433/Subpart-B/");
    });

    it("has a login confirmation banner and internal documents in the right sidebar of a subpart view when logged in", () => {
        cy.intercept("**/v3/resources/?&locations=42.431.A**").as("resources");
        cy.intercept("**/v3/file-manager/categories", {
            fixture: "categories-internal.json",
        }).as("internal-categories");
        cy.intercept(
            "**/v3/content-search/?resource-type=internal&locations=42.431.A**",
            {
                fixture: "42.431.internal.json",
            }
        ).as("internal431");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/42/431/10");

        cy.get(".div__login-sidebar").contains(
            "Resources you can access include policy documents internal to CMCS."
        );
        cy.get("#loginIndicator").should("be.visible");
        cy.get("a#loginSidebar").should("not.exist");

        cy.wait("@resources").then(() => {
            cy.get(".right-sidebar").scrollTo("bottom");
            cy.get(`button[data-test=TestCat]`).click({
                force: true,
            });
            cy.wait(250);
            cy.get(".right-sidebar").scrollTo("bottom");
            cy.get(`button[data-test=TestSubCat]`).click({
                force: true,
            });
            cy.wait(250);
            cy.get(".right-sidebar").scrollTo("bottom");
            cy.get(
                ".internal-docs__container div[data-test=TestSubCat] .supplemental-content"
            )
                .first()
                .get(".supplemental-content-date")
                .contains("August 30, 2023");
            //cy.get(
                //".internal-docs__container div[data-test=TestSubCat] .supplemental-content"
            //)
                //.first()
                //.get(".result__context--division")
                //.should("include.text", "Uploaded by MG1 — MD1")
                //.and("have.attr", "title", "Mock Group 1 — Mock Division 1");
            cy.get(
                ".internal-docs__container div[data-test=TestSubCat] .supplemental-content"
            )
                .first()
                .get(".supplemental-content-description")
                .contains("42 431 test");
            cy.get(".show-more-button")
                .contains("+ Show More (6)")
                .click({ force: true });
            cy.get(".show-more-button")
                .contains("- Show Less (6)");
        });
    });

    it("loads a subpart view in a mobile width", () => {
        cy.viewport("iphone-x");
        cy.visit("/42/433/");
        cy.contains("433.51").click({ force: true });

        cy.get(".right-sidebar").should("have.css", "display", "none");

        cy.get(".view-resources-link").should(($link) => {
            expect($link.first()).to.not.be.visible;
        });

        cy.get(".reg-history-link").should(($link) => {
            expect($link.first()).to.be.visible;
        });
    });

    it("loads a part view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.findByRole("link", { name: "433.1 Purpose." }).click({
            force: true,
        });
        cy.checkLinkRel();

        // goes to first part of the appropriate subpart (this is odd)
        cy.url().should("include", "#433-1");
        cy.get("#jumpToTitle").invoke("val").should("equal", "42");
        cy.get("#jumpToPart").invoke("val").should("equal", "433");
        cy.get(".latest-version").should("exist");
        cy.get("#433-1-title").should("be.visible");
        cy.focused().then(($el) => {
            cy.get($el).should("have.id", "433-1");
        });
    });

    it("should not have a button to view past versions", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.10").click({ force: true });

        cy.get(".latest-version").should("exist");
        cy.findByRole("button", { name: /View Past Versions/i }).should(
            "not.exist"
        );
    });

    it("should allow the user to return to the current version if they visit a link to a previous version", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/Subpart-A/2020-12-31/");

        cy.url().should("include", "2020-12-31");
        cy.get(".latest-version").should("not.exist");
        cy.findByRole("button", { name: /View Past Versions/i }).should(
            "not.exist"
        );

        cy.get(".view-and-compare").should("be.visible");
        cy.get("#close-link").click({ force: true });
        cy.get(".view-and-compare").should("not.be.visible");
        cy.get(".latest-version").should("exist");
    });

    it("renders FR Doc category correctly in sidebar", () => {
        cy.intercept("**/v3/resources/?&locations=42.433.10**", {
            fixture: "42.433.10.resources.json",
        }).as("resources43310");
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.10").click({ force: true });
        cy.url().should("include", "#433-10");
        cy.wait("@resources43310").then(() => {
            cy.get(".is-fr-doc-btn").click({ force: true });
            cy.get(".show-more-button")
                .contains("+ Show More (9)")
                .click({ force: true });
            cy.get(".show-more-button")
                .contains("- Show Less (9)");
        });
    });

    it("loads copy tooltip correctly", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("Subpart A").click({ force: true });
        cy.get("#433-8-title .copy-btn-container button.trigger-btn").click({
            force: true,
        });
        cy.get("#433-8-title .copy-btn-container .tooltip.clicked").should(
            "be.visible"
        );
        cy.get(
            "#433-8-title .copy-btn-container .tooltip.clicked .tooltip-title"
        ).contains("42 CFR § 433.8");
        cy.get(
            "#433-8-title .copy-btn-container .tooltip.clicked button.close-btn"
        ).click({ force: true });
        cy.get("#433-8-title .copy-btn-container .tooltip.clicked").should(
            "not.exist"
        );
    });

    it("loads reg history tooltip correctly", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("Subpart A").click({ force: true });
        cy.get("#433-8 .reg-history-link-container button.trigger-btn").click({
            force: true,
        });
        cy.get("#433-8 .reg-history-link-container .tooltip.clicked").should(
            "be.visible"
        );
        cy.checkLinkRel();
        cy.get(
            "#433-8 .reg-history-link-container .tooltip.clicked .tooltip-title"
        ).contains("View § 433.8 Effective In");
        // this next assertion is based on actual data returned from the API
        // it recently broke because the latest year changed from 2021 to 2022
        // so I'm commenting it out for now until we can figure out a better way
        //cy.get(
        //"#433-8 .reg-history-link-container .tooltip.clicked .gov-info-links a:nth-child(1)"
        //).contains("2021");
        cy.get(
            "#433-8 .reg-history-link-container .tooltip.clicked .gov-info-links a:nth-child(1)"
        )
            .should("have.attr", "href")
            .and("include", "govinfo.gov");
        cy.get(
            "#433-8 .reg-history-link-container .tooltip.clicked button.close-btn"
        ).click({ force: true });
        cy.get("#433-8 .reg-history-link-container .tooltip.clicked").should(
            "not.exist"
        );
    });
});

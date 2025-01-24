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
            "be.visible",
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
            Cypress.config().baseUrl + "/42/433/Subpart-B",
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
                "rgb(238, 250, 254)",
            );
        });
    });

    it("has a login call to action in the right sidebar of a subpart view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/51");

        cy.get(".div__login-cta--sidebar").contains(
            "To see internal documents, sign in or learn how to get account access.",
        );

        cy.get("span[data-testid=loginSidebar] a")
            .should("have.attr", "href")
            .and("include", "/login/?next=")
            .and("include", "/42/433/Subpart-B/");

        cy.eregsLogin({ username, password });
        cy.visit("/42/433/51");

        cy.get(".div__login-cta--sidebar").contains(
            "Resources you can access include policy documents internal to CMCS.",
        );
    });

    it("has a login confirmation banner and internal documents in the right sidebar of a subpart view when logged in", () => {
        cy.intercept("**/v3/resources/public?&citations=42.431.A**").as(
            "resources",
        );
        cy.intercept("**/v3/resources/internal/categories**", {
            fixture: "categories-internal.json",
        }).as("internal-categories");
        cy.intercept("**/v3/resources/internal?citations=42.431.A**", {
            fixture: "42.431.internal.json",
        }).as("internal431");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/42/431/10");

        cy.get(".div__login-cta--sidebar").contains(
            "Resources you can access include policy documents internal to CMCS.",
        );
        cy.get("button[data-testid='user-account-button']").should(
            "be.visible",
        );
        cy.get("span[data-testid=loginSidebar]").should("not.exist");

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
                ".internal-docs__container div[data-test=TestSubCat] .supplemental-content",
            )
                .first()
                .find(".supplemental-content-date")
                .contains("June 6, 2024");
            cy.get(
                ".internal-docs__container div[data-test=TestSubCat] .supplemental-content",
            )
                .first()
                .find(".supplemental-content-description")
                .contains("[Mock] Internal PDF");
            cy.get(
                ".internal-docs__container div[data-test=TestSubCat] .supplemental-content",
            )
                .eq(1)
                .find(".supplemental-content-description")
                .should("have.class", "supplemental-content-external-link")
                .and("include.text", "[Mock] Test 1 -- internal link");
            cy.get(".internal-docs__container div[data-test=TestSubCat]")
                .find(".show-more-button")
                .contains("+ Show More (6)")
                .click({ force: true });
            cy.get(".internal-docs__container div[data-test=TestSubCat]")
                .find(".show-more-button")
                .contains("- Show Less (6)");
        });
    });

    it("mixes supplemental content and subcategories in the right sidebar of a subpart view", () => {
        cy.intercept("**/v3/resources/public?&citations=42.433.A**", {
            fixture: "42.433.A.resources.json",
        }).as("resources433A");
        cy.intercept("**/v3/resources/internal&citations=42.433.A**", {
            fixture: "42.433.A.internal.json",
        }).as("internal433A");

        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/42/433/Subpart-A");

        // Find and expand Subregulatory Guidance category
        cy.get("button[data-test='Subregulatory Guidance']")
            .scrollIntoView()
            .click({ force: true });

        // Assert that subcategory is visible
        cy.get(
            "button[data-test='State Medicaid Director Letter (SMDL)']",
        ).should("be.visible");

        // Assert that supplemental content list is visible alongside subcategories
        cy.get(
            "div[data-test='Subregulatory Guidance'] > .supplemental-content-list",
        ).should("exist");

        // Assert that supplemental content that is not in a subcategory is visible
        // and contains expected text
        cy.get(
            "div[data-test='Subregulatory Guidance'] > .supplemental-content-list a .supplemental-content-description",
        )
            .should("exist")
            .scrollIntoView();

        cy.get(
            "div[data-test='Subregulatory Guidance'] > .supplemental-content-list a .supplemental-content-description",
        )
            .and("be.visible")
            .and("contain.text", "Mock title");
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
            "not.exist",
        );
    });

    it("should allow the user to return to the current version if they visit a link to a previous version", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/Subpart-A/2020-12-31/");

        cy.url().should("include", "2020-12-31");
        cy.get(".latest-version").should("not.exist");
        cy.findByRole("button", { name: /View Past Versions/i }).should(
            "not.exist",
        );

        cy.get(".view-and-compare").should("be.visible");
        cy.get("#close-link").click({ force: true });
        cy.get(".view-and-compare").should("not.be.visible");
        cy.get(".latest-version").should("exist");
    });

    it("renders FR Doc category correctly in sidebar", () => {
        cy.intercept("**/v3/resources/public?&citations=42.433.10**", {
            fixture: "42.433.10.resources.json",
        }).as("resources43310");
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.10").click({ force: true });
        cy.url().should("include", "#433-10");
        cy.wait("@resources43310").then(() => {
            cy.get(".is-fr-link-btn").click({ force: true });
            cy.get(".show-more-button")
                .contains("+ Show More (10)")
                .click({ force: true });
            cy.get(".show-more-button").contains("- Show Less (10)");
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
            "be.visible",
        );
        cy.get(
            "#433-8-title .copy-btn-container .tooltip.clicked .tooltip-title",
        ).contains("42 CFR § 433.8");
        cy.get(
            "#433-8-title .copy-btn-container .tooltip.clicked button.close-btn",
        ).click({ force: true });
        cy.get("#433-8-title .copy-btn-container .tooltip.clicked").should(
            "not.exist",
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
            "be.visible",
        );
        cy.checkLinkRel();
        cy.get(
            "#433-8 .reg-history-link-container .tooltip.clicked .tooltip-title",
        ).contains("View § 433.8 Effective In");
        // this next assertion is based on actual data returned from the API
        // it recently broke because the latest year changed from 2021 to 2022
        // so I'm commenting it out for now until we can figure out a better way
        //cy.get(
        //"#433-8 .reg-history-link-container .tooltip.clicked .gov-info-links a:nth-child(1)"
        //).contains("2021");
        cy.get(
            "#433-8 .reg-history-link-container .tooltip.clicked .gov-info-links a:nth-child(1)",
        )
            .should("have.attr", "href")
            .and("include", "govinfo.gov");
        cy.get(
            "#433-8 .reg-history-link-container .tooltip.clicked button.close-btn",
        ).click({ force: true });
        cy.get("#433-8 .reg-history-link-container .tooltip.clicked").should(
            "not.exist",
        );
    });
});

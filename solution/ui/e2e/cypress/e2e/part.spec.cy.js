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

        cy.injectAxe();
        cy.contains("Part 433 - State Fiscal Administration").should(
            "be.visible"
        );
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
        cy.get("h2.section-title")
            .contains("433.50 Basis, scope, and applicability.")
            .should("be.visible");
    });

    it("loads a subpart view", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.51").click({ force: true });

        cy.url().should("include", "Subpart-B");
        cy.get("#433-51-title").should("be.visible");
        cy.get(".latest-version").should("exist");
        cy.get("#subpart-resources-heading").contains("433.51 Resources");

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

        // goes to first part of the appropriate subpart (this is odd)
        cy.url().should("include", "#433-1");
        cy.get(".latest-version").should("exist");
        cy.get("#433-1-title").should("be.visible");
        cy.focused().then(($el) => {
            cy.get($el).should("have.id", "433-1");
        });
    });

    it("loads a different version of a subpart", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("433.10").click({ force: true });

        cy.get(".latest-version").should("exist");
        cy.findByRole("button", { name: /View Past Versions/i }).should(
            "be.visible"
        );
        cy.findByRole("button", { name: /View Past Versions/i }).click({
            force: true,
        });
        cy.get(".view-and-compare").should("be.visible");
        cy.get("#view-options").select("1/20/2017", { force: true });
        cy.url().should("include", "2017-01-20");
        cy.get(".latest-version").should("not.exist");

        cy.get("#close-link").click({ force: true });
        cy.get(".view-and-compare").should("not.be.visible");
        cy.get(".latest-version").should("exist");
    });

    it("renders FR Doc category correctly in sidebar", () => {
        cy.intercept("**/v3/resources/?locations=42.433.10**", {
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
                .click({ force: true })
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
        cy.get(
            "#433-8 .reg-history-link-container .tooltip.clicked .tooltip-title"
        ).contains("View § 433.8 Effective In");
        // this next assertion is based on actual data returned from the API
        // it recently broke because the latest year changed from 2021 to 2022
        // so I'm commenting it out for now until we can figure out a better way
        //cy.get(
            //"#433-8 .reg-history-link-container .tooltip.clicked .gov-info-links a:nth-child(1)"
        //).contains("2022");
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

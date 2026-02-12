describe("Part View", () => {
    beforeEach(() => {
        cy.env(["DEPLOYING"]).then(({ DEPLOYING }) => {
            cy.clearIndexedDB();
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = DEPLOYING;
            }).as("headers");
        });
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

        cy.get(".login-cta__div--sidebar").contains(
            "To see internal documents, sign in or learn how to get account access.",
        );

        cy.get("span[data-testid=loginSidebar] a")
            .should("have.attr", "href")
            .and("include", "/login/?next=")
            .and("include", "/42/433/Subpart-B/");
        cy.get("a.access__anchor")
            .should("have.attr", "href")
            .and("include", "/get-account-access/");
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
        cy.env(["TEST_USERNAME", "TEST_PASSWORD"]).then(({ TEST_USERNAME, TEST_PASSWORD }) => {
            cy.eregsLogin({
                username: TEST_USERNAME,
                password: TEST_PASSWORD
            });
            cy.visit("/42/431/10");

            cy.get(".login-cta__div--sidebar").contains(
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
                    .first()
                    .find(".supplemental-content-description .result__link--file-type")
                    .should("include.text", "PDF");
                cy.get(
                    ".internal-docs__container div[data-test=TestSubCat] .supplemental-content",
                )
                    .first()
                    .find(".supplemental-content-description .result__link--domain")
                    .should("not.exist");
                cy.get(
                    ".internal-docs__container div[data-test=TestSubCat] .supplemental-content",
                )
                    .eq(1)
                    .find(".supplemental-content-description")
                    .should("have.class", "supplemental-content-external-link")
                    .and("include.text", "[Mock] Test 1 -- internal link");
                cy.get(
                    ".internal-docs__container div[data-test=TestSubCat] .supplemental-content",
                )
                    .eq(1)
                    .find(".supplemental-content-description .result__link--file-type")
                    .should("include.text", "PDF");
                cy.get(".internal-docs__container div[data-test=TestSubCat]")
                    .find(".show-more-button")
                    .contains("+ Show More (6)")
                    .click({ force: true });
                cy.get(
                    ".internal-docs__container div[data-test=TestSubCat] .show-more-content .supplemental-content",
                )
                    .first()
                    .find(".supplemental-content-description .result__link--file-type")
                    .should("include.text", "PDF");
                cy.get(".internal-docs__container div[data-test=TestSubCat]")
                    .find(".show-more-button")
                    .contains("- Show Less (6)");
            });
        });
    });

    it("has Show/Hide Subjects button when supplemental content has subjects", () => {
        cy.intercept("**/v3/resources/public?&citations=42.433.A**", {
            fixture: "42.433.A.resources.json",
        }).as("resources433A");
        cy.viewport("macbook-15");
        cy.visit("/42/433/Subpart-A");

        // Find and expand Subregulatory Guidance category
        cy.get("button[data-test='Subregulatory Guidance']")
            .scrollIntoView();
        cy.get("button[data-test='Subregulatory Guidance']")
            .click({ force: true });

        cy.get("button[data-test='State Medicaid Director Letter (SMDL)']")
            .click({ force: true });

        cy.get("button.supplemental-content-subjects")
            .first()
            .should("be.visible")
            .and("contain.text", "Show Related Subjects");

        // first SMDL object has subjects
        cy.get("div[data-test='State Medicaid Director Letter (SMDL)']")
            .find(".supplemental-content")
            .eq(0)
            .find("button.supplemental-content-subjects")
            .should("exist");

        // second SMDL object does not have subjects
        cy.get("div[data-test='State Medicaid Director Letter (SMDL)']")
            .find(".supplemental-content")
            .eq(1)
            .should("exist")
            .find("button.supplemental-content-subjects")
            .should("not.exist");

        // click to show subjects
        cy.get("button.supplemental-content-subjects")
            .first()
            .click({ force: true });

        cy.get("button.supplemental-content-subjects")
            .first()
            .should("contain.text", "Hide Related Subjects");

        // Assert that subjects are visible
        cy.get("a[data-testid='add-subject-chip-19']")
            .should("be.visible")
            .and("contain.text", "Reports and Evaluations");

        // click on a subject chip
        cy.get("a[data-testid='add-subject-chip-19']")
            .click({ force: true });

        // Assert that the new URL includes the subject ID
        cy.url().should("include", "/subjects/?subjects=19");
    });

    it("mixes supplemental content and subcategories in the right sidebar of a subpart view", () => {
        cy.intercept("**/v3/resources/public?&citations=42.433.A**", {
            fixture: "42.433.A.resources.json",
        }).as("resources433A");
        cy.intercept("**/v3/resources/internal&citations=42.433.A**", {
            fixture: "42.433.A.internal.json",
        }).as("internal433A");

        cy.viewport("macbook-15");
        cy.env(["TEST_USERNAME", "TEST_PASSWORD"]).then(({ TEST_USERNAME, TEST_PASSWORD }) => {
            cy.eregsLogin({
                username: TEST_USERNAME,
                password: TEST_PASSWORD
            });
            cy.visit("/42/433/Subpart-A");

            // Find and expand Subregulatory Guidance category
            cy.get("button[data-test='Subregulatory Guidance']")
                .scrollIntoView();
            cy.get("button[data-test='Subregulatory Guidance']")
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
        cy.get("a#landing-nav-433-1").click({
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
        cy.get("#view-button").should("not.exist");
    });

    it("should allow the user to return to the current version if they visit a link to a previous version", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/433/Subpart-A/2020-12-31/");

        cy.url().should("include", "2020-12-31");
        cy.get(".latest-version").should("not.exist");
        cy.get("#view-button").should("not.exist");

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

    it.skip("loads an appendix view type without a right sidebar", () => {
        cy.viewport("macbook-15");
        cy.visit("45/75/Appendix-I-to-Part-75/#Appendix-I-to-Part-75");
        cy.checkLinkRel();

        cy.get("#jumpToTitle").invoke("val").should("equal", "45");
        cy.get("#jumpToPart").invoke("val").should("equal", "75");
        cy.get(".latest-version").should("exist");
        cy.get(".right-sidebar").should("not.exist");

        cy.focused().then(($el) => {
            cy.get($el).should("have.id", "Appendix-I-to-Part-75");
            cy.get($el).should(
                "have.css",
                "background-color",
                "rgb(238, 250, 254)",
            );
        });

        // copy tooltip works as expected
        cy.get("#Appendix-I-to-Part-75-title .copy-btn-container button.trigger-btn").click({
            force: true,
        });
        cy.get("#Appendix-I-to-Part-75-title .copy-btn-container .tooltip.clicked").should(
            "be.visible",
        );
        cy.get(
            "#Appendix-I-to-Part-75-title .copy-btn-container .tooltip.clicked .tooltip-title",
        ).contains("45 CFR Appendix I to Part 75");
        cy.get(
            "#Appendix-I-to-Part-75-title .copy-btn-container .tooltip.clicked button.close-btn",
        ).click({ force: true });
        cy.get("#Appendix-I-to-Part-75-title .copy-btn-container .tooltip.clicked").should(
            "not.exist",
        );
    });

    it("loads version history content correctly", () => {
        cy.intercept("**/v3/title/42/part/433/history/section/8", {
            fixture: "42.433.8.annual-editions.json",
        }).as("history433");
        cy.intercept("**/v3/title/42/part/433/versions/section/8", {
            fixture: "42.433.8.version-history.json",
        }).as("history433");
        cy.viewport("macbook-15");
        cy.visit("/42/433/");
        cy.contains("Subpart A").click({ force: true });
        cy.get("#433-8 div.collapse-content[data-test='433.8 section history']").should(
            "not.be.visible",
        );
        cy.get("#433-8 .reg-history-link button.collapsible-title").click({
            force: true,
        });
        cy.get("#433-8 div.collapse-content[data-test='433.8 section history']").should(
            "be.visible",
        );
        cy.get("#433-8 button[data-testid='version-history-tab']")
            .invoke("attr", "aria-selected")
            .should("eq", "true");
        cy.get("#433-8 button[data-testid='annual-editions-tab']")
            .invoke("attr", "aria-selected")
            .should("eq", "false");
        cy.checkLinkRel();
        cy.get(
            "#433-8 .version-history__container .version-history-items__container .version-history-item__date",
        ).contains("Jan 1, 2020");
        cy.get(
            "#433-8 .version-history__container .version-history-items__container .version-history-item__date a",
        )
            .should("have.attr", "href")
            .and("include", "https://www.ecfr.gov/on/2020-01-01/title-42/section-433.8");
        cy.get(
            "#433-8 .version-history__container .version-history-items__container .version-history__source",
        ).contains("Source: eCFR Point-in-Time System");
        cy.get(
            "#433-8 .version-history__container .version-history-items__container .version-history__source a",
        )
            .should("have.attr", "href")
            .and("include", "https://www.ecfr.gov/reader-aids/using-ecfr/ecfr-changes-through-time");
        cy.get("#433-8 button[data-testid='annual-editions-tab']")
            .click({ force: true });
        cy.checkLinkRel();
        cy.get(
            "#433-8 .version-history__container .gov-info-links-container",
        ).contains("Source: CFR Annual Edition");
        cy.get(
            "#433-8 .version-history__container .gov-info-links a:nth-child(1)",
        )
            .should("have.attr", "href")
            .and("include", "govinfo.gov")
            .and("include", "CFR-1997");
        cy.get("#433-8 .reg-history-link button.collapsible-title").click({
            force: true,
        });
        cy.get("#433-8 div.collapse-content[data-test='433.8 section history']").should(
            "not.be.visible",
        );
    });
});

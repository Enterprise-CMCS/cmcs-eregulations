const mainContentId = "#main-content";

describe("Homepage", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
        cy.intercept("**/v3/resources/public/categories**", {
            fixture: "categories.json",
        }).as("categories");
        cy.intercept(
            "**/v3/resources/public/federal_register_links?page=1&page_size=7**",
            { fixture: "frdocs.json" },
        ).as("frdocs");
        cy.intercept("**/v3/resources/public/links?page=1&page_size=7**", {
            fixture: "recent-guidance.json",
        }).as("recentGuidance");
    });

    it("loads the homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.contains("Medicaid & CHIP eRegulations");
        cy.checkLinkRel();
        cy.injectAxe();
        cy.checkAccessibility();

        cy.get("#jumpToTitle").should("have.value", "42");
        cy.get("#jumpToPart").should("not.have.attr", "disabled");
        cy.get("#jumpBtn").should("have.class", "active");
    });

    it("has a hidden Skip to main content link", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".ds-c-skip-nav").then(($el) => {
            const rect = $el[0].getBoundingClientRect();
            expect(rect.bottom).to.equal(-56); // hidden off-screen
        });
    });

    it("should have a div id on the page that matches the href of the skip to main content link", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".ds-c-skip-nav").should("have.attr", "href", mainContentId);
        cy.get(mainContentId).should("exist");
    });

    it("focuses and displays the Skip to main content link after tab is pressed one time", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("body").tab();
        cy.wait(500); // animation
        cy.focused().should("have.attr", "class", "ds-c-skip-nav");
        cy.focused().then(($el) => {
            const rect = $el[0].getBoundingClientRect();
            expect(rect.top).to.equal(0);
        });
    });

    it("has grouped FR docs in Related Rules tab", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".resources__container").should("exist");
        cy.get(".resources__container .v-tabs")
            .contains("Recent Rules")
            .click({ force: true });

        cy.get(".recent-rules-descriptive-text")
            .first()
            .should(($el) => {
                expect($el.text().trim()).to.equal(
                    "Includes 42 CFR 400, 430-460, 483, 600; 45 CFR 75, 95, 155-156",
                );
            });

        cy.get(".related-rule").should("have.length", 7);
        cy.get(".related-rule.ungrouped").then(($els) => {
            expect($els).to.have.length(3);
            cy.wrap($els[1]).find(".recent-title").should("exist");
            cy.wrap($els[1])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("Final");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(2, 102, 102)");
                });
            // assert that ungrouped element has download chip
            cy.wrap($els[0])
                .find(".recent-title span[data-testid='download-chip-2023-12098']")
                .should("exist")
                .and("have.text", "PDF");
            // assert that ::after pseudo element is not present on ungrouped item
            cy.wrap($els[0])
                .find(".link-heading")
                .then(($el) => {
                    const after = window.getComputedStyle($el[0], "::after");
                    const content = after.getPropertyValue("content");
                    expect(content).to.equal("none");
                });
            cy.wrap($els[0])
                .find(".recent-title")
                .then(($el) => {
                    const after = window.getComputedStyle($el[0], "::after");
                    const content = after.getPropertyValue("content");
                    expect(content).to.equal("none");
                });
        });
        cy.get(".related-rule.grouped").then(($els) => {
            expect($els).to.have.length(4);
            cy.wrap($els[0]).find(".recent-title").should("not.exist");
            cy.wrap($els[0])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("WD");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(255, 255, 255)");
                });
            // assert that first grouped element has no download chip even
            // even though file url has a .pdf extension
            cy.wrap($els[0])
                .find(".recent-title span.result__link--file-type")
                .should("not.exist");
            // assert that ::after pseudo element is present on heading
            // and not title for grouped item
            cy.wrap($els[0])
                .find(".link-heading")
                .then(($el) => {
                    const after = window.getComputedStyle($el[0], "::after");
                    const content = after.getPropertyValue("content");
                    expect(content).to.include("url");
                });
            cy.wrap($els[0])
                .find(".recent-title")
                .should("not.exist");
        });

        cy.get(".resources__container")
            .contains("View More Changes")
            .should("not.exist");
    });

    it("Sets the label as Final, when correction and withdraw are both set to false", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".resources__container .v-tabs")
            .contains("Recent Rules")
            .click();
        cy.get(".related-rule.ungrouped").then(($els) => {
            cy.wrap($els[1]).find(".recent-title").should("exist");
            cy.wrap($els[1])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("Final");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(2, 102, 102)");
                });
        });
    });

    it("Sets the label as WD when Correction is false and Withdrawal is true", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".resources__container .v-tabs")
            .contains("Recent Rules")
            .click();
        cy.get(".related-rule.grouped").then(($els) => {
            cy.wrap($els[0]).find(".recent-title").should("not.exist");
            cy.wrap($els[0])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("WD");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(255, 255, 255)");
                    expect($flag)
                        .to.have.css("color")
                        .and.eq("rgb(91, 97, 107)");
                    expect($flag)
                        .to.have.css("border-color")
                        .and.eq("rgb(91, 97, 107)");
                    expect($flag).to.have.css("border-width").and.eq("1px");
                    expect($flag).to.have.css("border-style").and.eq("solid");
                });
        });
    });

    it("Sets the label as WD when Correction is true and Withdrawal is true", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".resources__container .v-tabs")
            .contains("Recent Rules")
            .click();
        cy.get(".related-rule.grouped").then(($els) => {
            cy.wrap($els[3]).find(".recent-title").should("not.exist");
            cy.wrap($els[3])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("WD");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(255, 255, 255)");
                    expect($flag)
                        .to.have.css("color")
                        .and.eq("rgb(91, 97, 107)");
                    expect($flag)
                        .to.have.css("border-color")
                        .and.eq("rgb(91, 97, 107)");
                    expect($flag).to.have.css("border-width").and.eq("1px");
                    expect($flag).to.have.css("border-style").and.eq("solid");
                });
        });
    });

    it("Sets the label as CORR when Correction is true and Withdrawal is false", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".resources__container .v-tabs")
            .contains("Recent Rules")
            .click();
        cy.get(".related-rule.ungrouped").then(($els) => {
            cy.wrap($els[0]).find(".recent-title").should("exist");
            cy.wrap($els[0])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("CORR");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(214, 215, 217)");
                });
        });
    });

    it("Does not include Part 75 when Title 45 is selected in Jump To", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("#jumpToTitle").select("45");
        cy.get("#jumpToPart").then(($select) => {
            const options = $select.find("option");
            const values = [...options].map((o) => o.value);
            expect(values).to.not.include("75");
        });
    });

    it("jumps to a regulation Part using the jump-to select", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.jumpToRegulationPart({ title: "45", part: "95" });
    });

    it("jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.jumpToRegulationPartSection({
            title: "42",
            part: "433",
            section: "40",
        });
    });

    it("clicks on Title 42 Part 430 in ToC and loads the page", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".toc__container").contains("Part 430").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/42/430/");
        cy.contains("Grants to States for Medical Assistance Programs");
    });

    it("clicks on Title 45 Part 95 in ToC and loads the page", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".toc__container .v-tabs").contains("Title 45").click();
        cy.get(".toc__container").contains("Part 95").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/45/95/");
        cy.contains(
            "General Administration—Grant Programs (Public Assistance, Medical Assistance and State Children's Health Insurance Programs)",
        );
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/430/");
        cy.goHome();
    });

    it("has the correct descriptive text", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".cta .about-text__container p").should(($el) => {
            expect($el.text().replace(/\s+/g, " ").trim()).to.equal(
                "eRegulations organizes together regulations, subregulatory guidance, and other related policy materials.",
            );
        });
    });

    it("takes you to the about page when clicking 'Learn About This Tool'", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".cta .about-text__container a")
            .contains("Learn About This Tool")
            .click();
        cy.url().should("eq", Cypress.config().baseUrl + "/about/");
    });

    it("takes you to the proper sample search", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".policy-materials__container a.sample-search-btn")
            .contains("Try a Sample Search")
            .click({ force: true });
        cy.url().should(
            "eq",
            Cypress.config().baseUrl +
                `/search/?q=%22public%20health%20emergency%22`,
        );
    });

    it("has Recent Subregulatory Guidance tab and results with clickable subjects and related citations", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".resources__container").should("exist");
        cy.wait("@categories");
        cy.get(".recent-rules-descriptive-text").should("not.exist");
        cy.get(".resources__container")
            .contains("View More Guidance")
            .should("not.exist");
        cy.get(".supplemental-content .supplemental-content-description")
            .first()
            .find(".result__link--file-type")
            .should("have.text", "PDF");
        cy.get(".document__subjects")
            .first()
            .next() // next element should not be related citations collapse btn
            .should("have.class", "spacer");
        cy.get(".document__subjects a")
            .eq(0)
            .should("have.text", "Administrative Claiming Fixture Value");

        cy.get(".document__subjects")
            .eq(1)
            .next() // next element should be related citations collapse btn
            .should("have.class", "collapsible-title")
            .and("have.attr", "data-test", "related citations collapsible 526")
            .next() // next element should be hidden collapse content div
            .should("have.class", "collapse-content")
            .and("have.class", "invisible");

        // display collapse content
        cy.get(".collapsible-title")
            .first()
            .click({ force: true });
        cy.get("button[data-test='related citations collapsible 526']")
            .next()
            .should("have.class", "collapse-content")
            .and("not.have.class", "invisible");

        // re-hide collapse content
        cy.get(".collapsible-title")
            .first()
            .click({ force: true });
        cy.get("button[data-test='related citations collapsible 526']")
            .next()
            .should("have.class", "collapse-content")
            .and("have.class", "invisible");

        cy.get(".document__subjects a")
            .eq(1)
            .should("have.text", "Cost Allocation");
        cy.get(`a[data-testid=add-subject-chip-157]`)
            .should("have.attr", "title")
            .and("include", "Public Assistance Cost Allocation");
        cy.get(`a[data-testid=add-subject-chip-157]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects/?subjects=157");
    });

    it("loads the last parser success date from the API endpoint and displays it in footer", () => {
        cy.intercept("**/v3/ecfr_parser_result/**").as("parserResult");
        cy.viewport("macbook-15");
        cy.visit("/");
        //cy.wait("@parserResult");
        cy.get(".last-updated-date")
            .invoke("text")
            .should("match", /^\w{3} (\d{1}|\d{2}), \d{4}$/);
    });

    it("should have an open left nav on load on desktop", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
    });

    it("should have a closed left nav on load on tablet", () => {
        cy.viewport(800, 1024);
        cy.visit("/");
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
    });

    it("should have a closed left nav on mobile", () => {
        cy.viewport("iphone-x");
        cy.visit("/");
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
    });

    it("should responsively open and close the left nav if user does not click open/close button", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport(800, 1024);
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
        cy.viewport("macbook-15");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
    });

    it("should keep left nav open if user explicitly expands it, even if screen width changes", () => {
        cy.viewport(800, 1024);
        cy.visit("/");
        cy.get("nav#leftNav").should("have.attr", "class", "closed");
        cy.get("button.nav-toggle__button").click({ force: true });
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport("macbook-15");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport(800, 1024);
        cy.get("nav#leftNav").should("have.attr", "class", "open");
        cy.viewport("iphone-x");
        cy.get("nav#leftNav").should("have.attr", "class", "open");
    });

    it("takes you to a google doc when you click the 'Contact the Team' link", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".contact__column a")
            .scrollIntoView();
        cy.get(".contact__column a")
            .should("have.attr", "href")
            .and("include", "https://docs.google.com");
    });

    it("takes you to a google doc when you click the 'Sign up for a session' link", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".signup__column a")
            .scrollIntoView();
        cy.get(".signup__column a")
            .should("have.attr", "href")
            .and("include", "https://docs.google.com");
    });
});

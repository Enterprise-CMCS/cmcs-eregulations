const mainContentId = "#main-content";

describe("Homepage", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
        });
        cy.intercept(
            "**/v3/resources/federal_register_docs?page=1&page_size=3&paginate=true",
            { fixture: "frdocs.json" }
        ).as("frdocs");
    });

    it("loads the homepage", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.injectAxe();
        cy.contains("Medicaid & CHIP eRegulations");
        cy.checkAccessibility();
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

    it("has a flash banner at the top with a link to a feedback survey", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("div.flash-banner").should("be.visible");

        cy.get("div.flash-banner .greeting")
            .invoke("text")
            // remove the space char
            .invoke("replace", /\u00a0/g, " ")
            .should("eq", "We welcome questions and suggestions — ");

        cy.get("div.flash-banner a").should("have.text", "give us feedback.");
    });

    it("hides the flash banner when scrolling down", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("div.flash-banner").should("be.visible");
        cy.get("body").tab();
        cy.focused().should("have.attr", "class", "ds-c-skip-nav");
        cy.focused().then(() => {
            cy.get(".ds-c-skip-nav").click({ force: true });
            cy.wait(500);
            cy.get("div.flash-banner").then(($el) => {
                const rect = $el[0].getBoundingClientRect();
                expect(rect.bottom).to.be.lessThan(1);
            });
        });
    });

    it("shows feedback form in modal when clicking feedback link in flash banner", () => {
        // feedback link is in banner
        cy.viewport("macbook-15");
        cy.visit("/");
        // modal doesn't exist
        cy.get("div.blocking-modal-content").should("not.be.visible");
        // click link
        cy.get("div.flash-banner a")
            .should("have.text", "give us feedback.")
            .click({ force: true });
        // modal exists
        cy.get("div.blocking-modal-content").should("be.visible");
        // make sure background is right color etc
        cy.get("div.blocking-modal").should(
            "have.css",
            "background-color",
            "rgba(0, 0, 0, 0.8)"
        );
        // a11y
        cy.injectAxe();
        cy.checkAccessibility();
        // query iframe source to make sure it's google forms
        cy.get(".blocking-modal-content iframe#iframeEl")
            .should("have.attr", "src")
            .then((src) => {
                expect(src.includes("docs.google.com/forms")).to.be.true;
            });
        // click close
        cy.get("button.close-modal")
            .should("be.visible")
            .click({ force: true });
        // modal doesn't exist again
        cy.get("div.blocking-modal-content").should("not.be.visible");
    });

    it("has the correct title and copy text", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".jump-to-label").should(
            "have.text",
            "Jump to Regulation Section"
        );
        cy.get(".hero-text").should(
            "have.text",
            "Explore this site as a supplement to existing policy tools. How this tool is updated."
        );
    });

    it("takes you to the about page when clicking how this tool is updated link", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".hero-text a").click();

        cy.url().should(
            "eq",
            Cypress.config().baseUrl + "/about/#automated-updates"
        );
    });

    it("jumps to a regulation Part using the jump-to select", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".jump-to-input select").select("433");
        cy.get(".jump-to > form").submit();

        cy.url().should("eq", Cypress.config().baseUrl + "/42/433/#433");
    });

    it("jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".jump-to-input select").should("be.visible").select("433");
        cy.get(".jump-to-input input.number-box").type("40");
        cy.get(".jump-to > form").submit();

        cy.url().should(
            "eq",
            Cypress.config().baseUrl + "/42/433/Subpart-A/2021-03-01/#433-40"
        );
    });

    it("clicks on part 430 and loads the page", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get("#homepage-toc").contains("Part 430").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/42/430/");
        cy.contains("Grants to States for Medical Assistance Programs");
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.visit("/42/430/");
        cy.contains("Medicaid & CHIP eRegulations").click();

        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });

    it("has grouped FR docs in the right sidebar", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".related-rule-list").should("exist");
        cy.get(".recent-rules-descriptive-text").should(
            "have.text",
            "Includes 42 CFR 400, 430-460"
        );
        cy.get(".related-rule").should("have.length", 7);
        cy.get(".related-rule.ungrouped").then(($els) => {
            expect($els).to.have.length(3);
            cy.wrap($els[0]).find(".recent-title").should("exist");
            cy.wrap($els[0])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("Final");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(2, 102, 102)");
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
        });
    });

    it("Sets the label as Final, when correction and withdraw are both set to false", () => {
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.get(".related-rule.ungrouped").then(($els) => {
            cy.wrap($els[0]).find(".recent-title").should("exist");
            cy.wrap($els[0])
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
        cy.get(".related-rule.grouped").then(($els) => {
            cy.wrap($els[1]).find(".recent-title").should("not.exist");
            cy.wrap($els[1])
                .find(".recent-flag")
                .then(($flag) => {
                    expect($flag).to.have.text("CORR");
                    expect($flag)
                        .to.have.css("background-color")
                        .and.eq("rgb(214, 215, 217)");
                });
        });
    });

    it("loads the last parser success date from the API endpoint and displays it in footer", () => {
        cy.intercept("**/v3/ecfr_parser_result/**").as("parserResult");
        cy.viewport("macbook-15");
        cy.visit("/");
        cy.wait("@parserResult");
        cy.get(".last-updated-date")
            .invoke("text")
            .should("match", /^\w{3} (\d{1}|\d{2}), \d{4}$/);
    });
});

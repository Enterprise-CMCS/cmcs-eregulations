describe("Left sidebar", () => {
    const desktopMin = 1024;
    const tabletMin = 768;

    const destination = "/42/431/";
    const testId = "Subpart-A";

    beforeEach(() => {
        cy.env(["DEPLOYING"]).then(({ DEPLOYING }) => {
            cy.intercept("/**", (req) => {
                req.headers["x-automated-test"] = DEPLOYING;
            });
        });
    })

    it("opens the section when the left nav subsection is clicked", () => {
        cy.viewport("macbook-15");
        cy.visit(destination);
        cy.checkLinkRel();
        cy.get(`h3#nav-Subpart-A`).click({ force: true })
        cy.get(`h1#subpart-resources-heading`).should(
            "contain.text",
            "Subpart A Resources"
        )
        cy.get(`a#nav-431-10.menu-section`).click({ force: true });
        cy.get(`h1#subpart-resources-heading`).should(
            "contain.text",
            "§ 431.10 Resources"
        )
    })

    it("collapses and expands on button click", () => {
        cy.viewport("macbook-15");
        cy.visit(destination);
        cy.get("aside[data-state-name=left-sidebar]").should(
            "have.attr",
            "data-state",
            "expanded"
        );

        cy.get(".toc-controls > button[data-set-state=collapsed").click({
            force: true,
        });

        cy.get("aside[data-state-name=left-sidebar]").should(
            "have.attr",
            "data-state",
            "collapsed"
        );

        cy.get(".toc-controls > button[data-set-state=expanded").click({
            force: true,
        });

        cy.get("aside[data-state-name=left-sidebar]").should(
            "have.attr",
            "data-state",
            "expanded"
        );
    });

    it("is EXPANDED on page load for viewports >= 1024px width", () => {
        cy.viewport(desktopMin, 768);
        cy.visit(destination);
        cy.get("aside[data-state-name=left-sidebar]").should(
            "have.attr",
            "data-state",
            "expanded"
        );
    });

    it("is COLLAPSED on page load for viewports < 1024px width", () => {
        cy.viewport(desktopMin - 1, 768);
        cy.visit(destination);
        cy.get("aside[data-state-name=left-sidebar]").should(
            "have.attr",
            "data-state",
            "collapsed"
        );
    });

    it("expands to full width for viewports < 768px width", () => {
        cy.viewport(tabletMin - 1, 768);
        cy.visit(destination);
        cy.document()
            .then((doc) => {
                return doc.documentElement.getBoundingClientRect();
            })
            .then((viewportRect) => {
                cy.visit(destination);
                cy.get(".toc-controls > button[data-set-state=expanded]").click(
                    {
                        force: true,
                    }
                );
                cy.get("aside[data-state-name=left-sidebar]")
                    .invoke("innerWidth")
                    .should("equal", viewportRect.width);
            });
    });

    it("sets correct classes for child when subpart is expanded or collapsed", () => {
        cy.viewport("macbook-15");
        cy.visit(destination);

        // ensure child has classes that set 0 height and display: none
        cy.get(`div[data-test=${testId}]`)
            .should("have.class", "invisible")
            .and("have.class", "display-none");

        // toggle open collapse content
        cy.get(`button[data-test=${testId}]`).click({ force: true });

        // wait for duration of transition
        cy.wait(0.5)

        // ensure collapse conteng no longer has classes
        // that set 0 height and display: none
        cy.get(`div[data-test=${testId}]`)
            .should("not.have.class", "invisible")
            .and("not.have.class", "display-none");
    });
});

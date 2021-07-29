describe("Left sidebar", () => {
    const desktopMin = 1024;
    const tabletMin = 768;

    const destination = "/42/431/";
    const testId = "Subpart-A";

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

    it("sets tabindex properly for subsections when subpart is expanded or collapsed", () => {
        cy.viewport("macbook-15");
        cy.visit(destination);

        cy.get(`li#${testId}`).within(($li) => {
            // get collapsed tabindex
            cy.get($li)
                .find("ul.toggle-toc-menu-sections a")
                .should("have.attr", "tabindex", "-1");

            // toggle open collapse content
            cy.get(`button[data-test=${testId}]`).click({ force: true });

            // get expanded tabindex
            cy.get($li)
                .find("ul.toggle-toc-menu-sections a")
                .should("have.attr", "tabindex", "0");
        });
    });
});

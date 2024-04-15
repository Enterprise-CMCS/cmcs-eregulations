describe("custom login page", { scrollBehavior: "center" }, () => {
    beforeEach(() => {
        cy.clearIndexedDB();
    });

    it("has a flash banner at the top with a link to a feedback survey", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.checkLinkRel();
        cy.injectAxe();
        cy.checkAccessibility();
        cy.checkFlashBanner();
    });

    it("shows feedback form in modal when clicking feedback link in flash banner", () => {
        // feedback link is in banner
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.checkBlockingModal();
    });

    it("custom-login-page - jumps to a regulation Part using the jump-to select", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.jumpToRegulationPart({ title: "45", part: "95" });
    });

    it("custom-login-page - jumps to a regulation Part section using the section number text input", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.jumpToRegulationPartSection({
            title: "42",
            part: "433",
            section: "40",
        });
    });

    it("allows a user to go back to the homepage by clicking the top left link", () => {
        cy.viewport("macbook-15");
        cy.visit("/login");
        cy.goHome();
    });
});

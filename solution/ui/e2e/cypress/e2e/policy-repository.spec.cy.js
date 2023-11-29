const TITLE_42 = 42;
const TITLE_45 = 45;

const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");
const readerUsername = Cypress.env("READER_USERNAME");
const readerPassword = Cypress.env("READER_PASSWORD");

const _beforeEach = () => {
    cy.intercept("/**", (req) => {
        req.headers["x-automated-test"] = Cypress.env("DEPLOYING");
    });

    cy.intercept("**/v3/titles", [TITLE_42, TITLE_45]).as("titles");

    cy.intercept(`**/v3/title/${TITLE_42}/parts`, {
        fixture: "parts-42.json",
    }).as("parts42");

    cy.intercept(`**/v3/title/${TITLE_45}/parts`, {
        fixture: "parts-45.json",
    }).as("parts45");

    cy.intercept("**/v3/file-manager/subjects", {
        fixture: "subjects.json",
    }).as("subjects");
};

Cypress.Commands.add("getPolicyDocs", ({ username, password }) => {
    cy.intercept("**/v3/content-search/?q=mock**", {
        fixture: "policy-docs.json",
    }).as("subjectFiles");
    cy.viewport("macbook-15");
    cy.eregsLogin({ username, password });
    cy.visit("/policy-repository/?q=mock");
    cy.injectAxe();
    cy.wait("@subjectFiles").then((interception) => {
        expect(interception.response.statusCode).to.eq(200);
    });
});

describe("Policy Repository", () => {
    beforeEach(_beforeEach);

    it("shows the login screen when you visit /policy-repository/ without logging in", () => {
        cy.viewport("macbook-15");
        cy.visit("/policy-repository/");
        cy.url().should("include", "/admin/login");
    });

    it("show the policy repository page when logged in", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.url().should("include", "/policy-repository/");
        cy.get("#loginIndicator").should("be.visible");
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] a"
        ).scrollIntoView();
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] div.subj-toc-li__count"
        )
            .should("be.visible")
            .and("have.text", "0 public and 1 internal resources ");
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-63] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", " Managed Care ")
            .click({ force: true });
        cy.url().should("include", "/policy-repository?subjects=63");
        cy.get(`button[data-testid=add-subject-2]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=2");
    });

    it("should make a successful request to the content-search endpoint", () => {
        cy.intercept("**/v3/content-search/?**").as("files");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.url().should("include", "/policy-repository/");
        cy.get(".subj-toc__list li:nth-child(1) a").click({ force: true });
        cy.wait("@files").then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
        });
    });

    it("loads the correct subject and search query when the URL is changed", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.url().should("include", "/policy-repository/");

        cy.get(`button[data-testid=add-subject-1]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=1");
        cy.get(`button[data-testid=remove-subject-1]`).should("exist");

        cy.get(`button[data-testid=add-subject-2]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=2");
        cy.get(`button[data-testid=remove-subject-2]`).should("exist");

        cy.get(`button[data-testid=add-subject-3]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=3");
        cy.get(`button[data-testid=remove-subject-3]`).should("exist");

        cy.go("back");
        cy.url().should("include", "/policy-repository?subjects=2");
        cy.get(`button[data-testid=remove-subject-3]`).should("not.exist");

        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get(".search-field .v-input__icon--append button").click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=2&q=test");

        cy.get(`button[data-testid=remove-subject-2]`).click({
            force: true,
        });
        cy.get(`button[data-testid=remove-subject-2]`).should("not.exist");
        cy.url().should("include", "/policy-repository?q=test");
    });

    it("should display and fetch the correct subjects on load if they are included in URL", () => {
        cy.getPolicyDocs({ username, password })
        cy.get(".related-sections")
            .first()
            .find(".related-section-link")
            .first()
            .find("a")
            .should("have.attr", "href")
            .and("not.include", "undefined")
            .and("include", "/42/435/116#435-116");
        cy.get(".result__link")
            .eq(0)
            .find("a")
            .should("not.include.text", "Download")
            .and("have.class", "external");
        cy.get(".result__link")
            .eq(1)
            .should("include.text", "Download")
            .find("a")
            .should("not.have.class", "external")
            .find(
                "span[data-testid=download-chip-d89af093-8975-4bcb-a747-abe346ebb274]"
            )
            .should("include.text", "Download MSG");

        cy.checkAccessibility();
    });
    it("should not display edit button for individual uploaded items if signed in and authorized to edit", () => {
        cy.getPolicyDocs({ username: readerUsername, password: readerPassword })
        cy.get(".edit-button").should("not.exist");
        cy.checkAccessibility();
    });
    it("should display edit button for individual uploaded items if signed in and authorized to edit", () => {
        cy.getPolicyDocs({ username, password })
        cy.get(".edit-button").should("exist");
        cy.checkAccessibility();
    });
    it("should visit the admin page for the document when the edit button is clicked", () => {
        cy.getPolicyDocs({ username, password })
        cy.retry(3, { interval: 1000 }, () => {
            cy.get('.edit-button').first().should('be.visible').click({ force: true });
            cy.wait(2000);
            cy.url({ timeout: 10000 }).should("include", "/admin/resources/supplementalcontent/610/change/");
        });
    });
    it("should update the URL when a subject chip is clicked", () => {
        cy.intercept("**/v3/content-search/**", {
            fixture: "policy-docs.json",
        }).as("subjectFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository/");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .uncheck({ force: true });
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .should("not.be.checked");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .should("be.checked");
        cy.url().should("include", "/policy-repository?type=internal");
        cy.get(`button[data-testid=add-subject-3]`).click({
            force: true,
        });
        cy.url().should(
            "include",
            "/policy-repository?type=internal&subjects=3"
        );
        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get(".search-field .v-input__icon--append button").click({
            force: true,
        });
        cy.url().should(
            "include",
            "/policy-repository?type=internal&subjects=3&q=test"
        );
        cy.get(`a[data-testid=add-subject-chip-4]`)
            .should("have.attr", "title")
            .and("include", "Adult Day Health");
        cy.get(`a[data-testid=add-subject-chip-4]`).click({
            force: true,
        });
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .should("be.checked");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .should("be.checked");
        cy.url().should("include", "/policy-repository?subjects=4&type=all");
        cy.get("input#main-content").should("have.value", "");
    });

    it("should display correct subject ID number in the URL if one is included in the URL on load and different one is selected via the Subject Selector", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository/?subjects=77");
        cy.url().should("include", "/policy-repository/?subjects=77");
        cy.get(`button[data-testid=remove-subject-77]`).should("exist");
        cy.get("button[data-testid=add-subject-63]").should(
            "not.have.class",
            "sidebar-li__button--selected"
        );
        cy.get("button[data-testid=add-subject-63]").click({
            force: true,
        });
        cy.get("button[data-testid=add-subject-63]").should(
            "have.class",
            "sidebar-li__button--selected"
        );
        cy.get(`button[data-testid=remove-subject-63]`).should("exist");
        cy.get(`button[data-testid=remove-subject-77]`).should("not.exist");
        cy.url().should("include", "/policy-repository?subjects=63");
    });

    it("should filter the subject list when a search term is entered into the subject filter", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository/");

        cy.injectAxe();

        cy.get(`button[data-testid=remove-subject-1]`).should("not.exist");
        cy.get(`button[data-testid=add-subject-1]`).should(
            "include.text",
            "Cures Act"
        );
        cy.get(`button[data-testid=clear-subject-filter]`).should(
            "not.be.visible"
        );

        cy.checkAccessibility();

        cy.get("input#subjectReduce")
            .should("exist")
            .should("have.value", "")
            .type("21", { force: true });
        cy.get(`button[data-testid=clear-subject-filter]`).should("exist");
        cy.get("input#subjectReduce").should("have.value", "21");
        cy.get(".subjects__list li").should("have.length", 1);
        cy.get(`button[data-testid=add-subject-1]`).should(
            "include.text",
            "21st Century Cures Act"
        );
        cy.get(`button[data-testid=add-subject-1]`).click({
            force: true,
        });
        cy.url().should("include", "/policy-repository?subjects=1");
        cy.get(`button[data-testid=remove-subject-1]`).should("exist");
        cy.get(`button[data-testid=clear-subject-filter]`).should("exist");

        cy.checkAccessibility();

        cy.get("input#subjectReduce")
            .type("{enter}", { force: true });

        cy.url().should("include", "/policy-repository?subjects=1");

        cy.get(`button[data-testid=clear-subject-filter]`).click({
            force: true,
        });
        cy.get("input#subjectReduce").should("have.value", "");
        cy.get(".subjects__list li").should("have.length", 78);
    });

    it("should display and fetch the correct search query on load if it is included in URL", () => {
        cy.intercept("**/v3/content-search/?q=test**").as("qFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository/?q=test");
        cy.wait("@qFiles").then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
        });
        cy.get("input#main-content").should("have.value", "test");
    });

    it("should have a Documents to Show checkbox list", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.get(".doc-type__toggle-container h3").should(
            "have.text",
            "Documents to Show"
        );
        cy.get(".doc-type__toggle fieldset").should("exist");
        cy.get(".doc-type__toggle fieldset > div").should("have.length", 2);
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("label")
            .should("have.text", "Public Resources");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .should("be.checked")
            .and("have.value", "external");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("label")
            .should("have.text", "Internal Resources");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .should("be.checked")
            .and("have.value", "internal");
    });

    it("should show only the Table of Contents if both or neither checkboxes are checked", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.get(".subj-toc__container").should("exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .uncheck({ force: true });
        cy.url().should("include", "/policy-repository?type=internal");
        cy.get(".subj-toc__container").should("not.exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .uncheck({ force: true });
        cy.get(".subj-toc__container").should("exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .check({ force: true });
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .check({ force: true });
        cy.url().should("include", "/policy-repository");
    });

    it("should not make a request to the content-search endpoint if both checkboxes are checked on load", () => {
        cy.intercept("**/v3/content-search/**").as("contentSearch");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.wait(2000);
        cy.get("@contentSearch.all").then((interception) => {
            expect(interception).to.have.length(0);
        });
    });

    it("goes to another SPA page from the policy repository page", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.clickHeaderLink({ page: "Resources", screen: "wide" });
        cy.url().should("include", "/resources");
    });

    it("returns you to the admin login page when you log out", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/policy-repository");
        cy.get("#logout").click();
        cy.get("#login-form").should("be.visible");
    });
});

describe("Policy Repository Search", () => {
    beforeEach(_beforeEach);

    it("shows the login screen when you visit /policy-repository/search without logging in", () => {
        cy.viewport("macbook-15");
        cy.visit("/policy-repository/search/");
        cy.url().should("include", "/admin/login");
    });

    it("show the policy repository search page when logged in", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/policy-repository/search",
        });
        cy.visit("/policy-repository/search");
        cy.url().should("include", "/policy-repository/search/");
        cy.get("#loginIndicator").should("be.visible");
    });

    it("should make a successful request to the content-search endpoint", () => {
        cy.intercept("**/v3/content-search/?**").as("queriedFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/policy-repository/search",
        });
        cy.visit("/policy-repository/search");
        cy.url().should("include", "/policy-repository/search/");
        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get(".search-field .v-input__icon--append button").click({
            force: true,
        });
        cy.url().should("include", "/policy-repository/search?q=test");
        cy.wait("@queriedFiles").then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
        });
    });
});
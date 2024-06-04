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

    cy.intercept("**/v3/file-manager/categories/tree", {
        fixture: "categories-internal-tree.json",
    }).as("internalCategories");

    cy.intercept("**/v3/resources/categories/tree", {
        fixture: "categories-tree.json",
    }).as("categories");
};

const _beforePaginate = () => {
    cy.intercept(
        "**/v3/content-search/?resource-type=external&page_size=50&paginate=true**",
        {
            fixture: "policy-docs-50-p1.json",
        }
    ).as("initialPage");

    cy.intercept("**/v3/content-search/?resource-type=external&page=1**", {
        fixture: "policy-docs-50-p1.json",
    }).as("page1");

    cy.intercept("**/v3/content-search/?resource-type=external&page=2**", {
        fixture: "policy-docs-50-p2.json",
    }).as("page2");
};

Cypress.Commands.add("getPolicyDocs", ({ username, password }) => {
    cy.intercept("**/v3/content-search/?q=mock**", {
        fixture: "policy-docs.json",
    }).as("subjectFiles");
    cy.viewport("macbook-15");
    cy.eregsLogin({ username, password, landingPage: "/subjects/" });
    cy.visit("/subjects/?q=mock");
    cy.injectAxe();
    cy.wait("@subjectFiles").then((interception) => {
        expect(interception.response.statusCode).to.eq(200);
    });
});

describe("Find by Subjects", () => {
    beforeEach(_beforeEach);

    it("redirects /policy-repository to /subjects", () => {
        cy.viewport("macbook-15");
        cy.visit("/policy-repository?subjects=2&q=test");
        cy.url().should("not.include", "/policy-repository");
        cy.url()
            .should("include", "/subjects/")
            .and("include", "subjects=2")
            .and("include", "q=test");
        cy.get(".div__login-sidebar a")
            .should("have.attr", "href")
            .and("include", "next")
            .and("include", "subjects/")
            .and("include", "q=test")
            .and("include", "subjects=2");
    });

    it("redirects /resources to /subjects", () => {
        cy.viewport("macbook-15");
        cy.visit("/resources?q=test");
        cy.url().should("not.include", "/resources");
        cy.url().should("include", "/subjects/").and("not.include", "q=test");
        cy.get(".div__login-sidebar a")
            .should("have.attr", "href")
            .and("include", "next")
            .and("include", "subjects/")
            .and("not.include", "q=test");
    });

    it("shows the custom eua login screen when you visit /subjects/ and click 'sign in'", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");
        cy.get(".div__login-sidebar a")
            .should("have.attr", "href")
            .and("include", "next")
            .and("include", "subjects/")
            .and("not.include", "q=");

        cy.get(".div__login-sidebar a").click();
        cy.url()
            .should("include", "/?next=")
            .and("include", "subjects/")
            .and("not.include", "q=");
    });

    it("should show only public items when logged out", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");

        cy.injectAxe();

        cy.get("button[data-testid='user-account-button']").should("not.exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .should("be.checked")
            .and("be.disabled");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .should("not.be.checked")
            .and("be.disabled");

        cy.checkAccessibility();

        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] a"
        ).scrollIntoView();
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] div.subj-toc-li__count"
        )
            .should("be.visible")
            .and("have.text", "0 public resources");
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-63] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", "Managed Care")
            .click({ force: true });
        cy.url().should("include", "/subjects?subjects=63");
        cy.get(".subject__heading")
            .should("exist")
            .and("have.text", "Managed Care");
        cy.url().should("include", "/subjects?subjects=63");
    });

    it("should strip document-type query parameter from URL when not logged in", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/?type=internal");
        cy.url().should("not.include", "type");
    });

    it("should show public and internal items when logged in", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");
        cy.url().should("include", "/subjects/");
        cy.get("button[data-testid='user-account-button']").should(
            "be.visible"
        );
        cy.get(".subject__heading").should("not.exist");
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] a"
        ).scrollIntoView();
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] div.subj-toc-li__count"
        )
            .should("be.visible")
            .and("have.text", "0 public and 1 internal resources");
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-63] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", "Managed Care")
            .click({ force: true });
        cy.url().should("include", "/subjects?subjects=63");
        cy.get(".subject__heading")
            .should("exist")
            .and("have.text", "Managed Care");
        cy.get(`button[data-testid=add-subject-2]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=2");
    });

    it("should display the appropriate results column header whether viewing keyword search results or viewing the items within a subject.", () => {
        cy.intercept("**/v3/content-search/**", {
            fixture: "policy-docs.json",
        }).as("subjectFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/subjects");
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-3] a")
            .should("have.text", "Access to Services")
            .click({ force: true });
        cy.url().should("include", "/subjects?subjects=3");
        cy.get(".subject__heading")
            .should("exist")
            .and("have.text", "Access to Services");
        cy.get("search-results__heading").should("not.exist");
        cy.get(".search-results-count").should(
            "have.text",
            "1 - 2 of 2 documents"
        );
        cy.get("input#main-content").type("test", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });
        cy.get(".subject__heading").should("not.exist");
        cy.get(".search-results__heading")
            .should("exist")
            .and("have.text", " Search Results ");
        cy.get(".search-results-count").should(
            "have.text",
            "1 - 2 of 2 results for test within Access to Services"
        );
        cy.get(`button[data-testid=remove-subject-3]`).click({
            force: true,
        });
        cy.get(".search-results-count").should(
            "have.text",
            "1 - 2 of 2 results for test"
        );
        cy.get("input#main-content").clear();
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .uncheck({ force: true });
        cy.get("search-results__heading").should("not.exist");
        cy.get(".subject__heading").should("not.exist");
        cy.get(".search-results-count").should(
            "have.text",
            "1 - 2 of 2 documents"
        );
    });

    it("should make a successful request to the content-search endpoint", () => {
        cy.intercept("**/v3/content-search/?**").as("files");
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");
        cy.url().should("include", "/subjects/");
        cy.get(".subj-toc__list li:nth-child(1) a").click({ force: true });
        cy.wait("@files").then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
        });
    });

    it("loads the correct subject and search query when the URL is changed", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });

        cy.visit("/subjects");
        cy.url().should("include", "/subjects/");

        cy.get(`button[data-testid=add-subject-1]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=1");
        cy.get(`button[data-testid=remove-subject-1]`).should("exist");
        cy.get(".subject__heading span")
            .eq(0)
            .should("have.text", "Cures Act")
            .and("have.class", "subj-heading__span--bold");
        cy.get(".subject__heading span")
            .eq(1)
            .should("have.text", "21st Century Cures Act")
            .and("not.have.class", "subj-heading__span--bold");

        cy.get(`button[data-testid=add-subject-2]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=2");
        cy.get(`button[data-testid=remove-subject-2]`).should("exist");
        cy.get(".subject__heading span")
            .eq(0)
            .should("have.text", "ABP")
            .and("have.class", "subj-heading__span--bold");
        cy.get(".subject__heading span")
            .eq(1)
            .should("have.text", "Alternative Benefit Plan")
            .and("not.have.class", "subj-heading__span--bold");

        cy.get(`button[data-testid=add-subject-3]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=3");
        cy.get(`button[data-testid=remove-subject-3]`).should("exist");
        cy.get(".subject__heading span")
            .eq(0)
            .should("have.text", "Access to Services")
            .and("have.class", "subj-heading__span--bold");
        cy.get(".subject__heading span").eq(1).should("not.exist");

        cy.go("back");
        cy.url().should("include", "/subjects?subjects=2");
        cy.get(`button[data-testid=remove-subject-3]`).should("not.exist");

        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=2&q=test");

        cy.get(`button[data-testid=remove-subject-2]`).click({
            force: true,
        });
        cy.get(`button[data-testid=remove-subject-2]`).should("not.exist");
        cy.url().should("include", "/subjects?q=test");
    });

    it("should display and fetch the correct subjects on load if they are included in URL", () => {
        cy.getPolicyDocs({ username, password });
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
        cy.get(".doc-type__label")
            .eq(0)
            .should("include.text", " Public")
            .find("i")
            .should("have.class", "fa-users");
        cy.get(".doc-type__label")
            .eq(1)
            .should("include.text", " Internal")
            .find("i")
            .should("have.class", "fa-key");

        cy.checkAccessibility();
    });

    it("should not display edit button for individual uploaded items if signed in and authorized to edit", () => {
        cy.getPolicyDocs({
            username: readerUsername,
            password: readerPassword,
        });
        cy.get(".edit-button").should("not.exist");
        cy.checkAccessibility();
    });

    it("should display edit button for individual uploaded items if signed in and authorized to edit", () => {
        cy.getPolicyDocs({ username, password });
        cy.get(".edit-button").should("exist");
        cy.checkAccessibility();
    });

    it("should update the URL when a subject chip is clicked", () => {
        cy.intercept("**/v3/content-search/**", {
            fixture: "policy-docs.json",
        }).as("subjectFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });

        cy.visit("/subjects/");
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
        cy.url().should("include", "/subjects?type=internal");
        cy.get(`button[data-testid=add-subject-3]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?type=internal&subjects=3");
        cy.get("input#main-content")
            .should("be.visible")
            .type("test search", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });
        cy.url().should(
            "include",
            "/subjects?type=internal&subjects=3&q=test+search"
        );
        cy.get(".search-form .form-helper-text .search-suggestion").should(
            "not.exist"
        );
        cy.get(".document__subjects a")
            .eq(0)
            .should("have.text", "Access to Services");
        cy.get(".document__subjects a")
            .eq(1)
            .should("have.text", "Adult Day Health");
        cy.get(".document__subjects a")
            .eq(2)
            .should("have.text", "Ambulatory Prenatal Care");
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
        cy.url().should("include", "/subjects?subjects=4&type=all");
        cy.get("input#main-content").should("have.value", "");
    });

    it("should display correct subject ID number in the URL if one is included in the URL on load and different one is selected via the Subject Selector", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects/?subjects=77");
        cy.url().should("include", "/subjects/?subjects=77");
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
        cy.url().should("include", "/subjects?subjects=63");
    });

    it("should filter the subject list when a search term is entered into the subject filter", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects/");

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
            .and("have.value", "")
            .and("have.attr", "placeholder", "Filter the subject list")
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
        cy.url().should("include", "/subjects?subjects=1");
        cy.get(`button[data-testid=remove-subject-1]`).should("exist");
        cy.get(`button[data-testid=clear-subject-filter]`).should("exist");

        cy.checkAccessibility();

        cy.get("input#subjectReduce").type("{enter}", { force: true });

        cy.url().should("include", "/subjects?subjects=1");

        cy.get(`button[data-testid=clear-subject-filter]`).click({
            force: true,
        });
        cy.get("input#subjectReduce").should("have.value", "");
        cy.get(".subjects__list li").should("have.length", 78);
    });

    it("should display and fetch the correct search query on load if it is included in URL", () => {
        cy.intercept(
            "**/v3/content-search/?q=streamlined%20modular%20certification**"
        ).as("qFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects/?q=streamlined%20modular%20certification");
        cy.wait("@qFiles").then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
        });
        cy.get("input#main-content").should(
            "have.value",
            "streamlined modular certification"
        );
        cy.get(".subject__heading").should("not.exist");
    });

    it("should have a Documents to Show checkbox list", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");
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
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");
        cy.get(".subj-toc__container").should("exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .uncheck({ force: true });
        cy.url().should("include", "/subjects?type=internal");
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
        cy.url().should("include", "/subjects");
    });

    it("should not make a request to the content-search endpoint if both checkboxes are checked on load", () => {
        cy.intercept("**/v3/content-search/**").as("contentSearch");
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");
        cy.wait(2000);
        cy.get("@contentSearch.all").then((interception) => {
            expect(interception).to.have.length(0);
        });
    });

    it("should not have a categories filter on initial load with no selected filter params", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");
        cy.get("div[data-testid='category-select']").should("not.exist");
    });

    it("should have a categories filter on initial load if page visited with a categories query param in URL", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/?categories=3");
        cy.get("div[data-testid='category-select']")
            .should("exist")
            .find(".v-select__selection")
            .should("have.text", "Related Statutes");
        cy.get("div[data-testid='category-select']")
            .find("label")
            .should("have.text", "Choose Category")
            .and("not.be.visible");
    });

    it("should only show category type labels when logged in", () => {
        cy.clearIndexedDB();
        cy.viewport("macbook-15");

        // Visit without authenticating
        cy.visit("/subjects?q=test");

        // Assert that category select label is visible
        cy.get("div[data-testid='category-select']")
            .should("exist")
            .find("label")
            .should("have.text", "Choose Category")
            .and("be.visible");

        // Open category select dropdown and assert that
        // Doc Type label does not exist
        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']")
            .find(".doc-type__label")
            .should("not.exist");

        // Assert that internal categories do not exist
        cy.get("div[data-testid='internal-0']").should("not.exist");

        // Log in and visit the same page
        cy.eregsLogin({ username, password, landingPage: "/subjects/" });
        cy.visit("/subjects?q=test");

        // Open category select dropdown and assert that
        // Doc Type label is visible
        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']")
            .find(".doc-type__label")
            .should("include.text", " Public")
            .find("i")
            .should("have.class", "fa-users");
        cy.get("div[data-testid='internal-0']")
            .should("exist")
            .scrollIntoView();
        cy.get("div[data-testid='internal-0']")
            .find(".doc-type__label")
            .should("include.text", " Internal")
            .find("i")
            .should("have.class", "fa-key");
    });

    it("should have a categories filter after selecting a subject, and not have a categories filter after removing the subject", () => {
        cy.clearIndexedDB();
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/subjects/" });
        cy.visit("/subjects/");

        // Assert that the category filter is not visible
        cy.get("div[data-testid='category-select']").should("not.exist");

        // Select subject
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-63] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", "Managed Care")
            .click({ force: true });

        // Assert that the category filter is visible
        cy.get("div[data-testid='category-select']")
            .should("exist")
            .find("label")
            .should("have.text", "Choose Category")
            .and("be.visible");

        // Remove subject
        cy.get("button[data-testid=remove-subject-63]").click({ force: true });

        // Assert that the category filter is not visible
        cy.get("div[data-testid='category-select']").should("not.exist");
    });

    it("should clear selected category if query string or subject is toggled", () => {
        cy.viewport("macbook-15");

        // Log in
        cy.eregsLogin({ username, password, landingPage: "/subjects/" });
        cy.visit("/subjects/");

        // Assert that category filter is not visible
        cy.get("div[data-testid='category-select']").should("not.exist");

        // Select a subject
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-63] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", "Managed Care")
            .click({ force: true });

        // Assert that the category filter is visible
        cy.get("div[data-testid='category-select']")
            .should("exist")
            .find("label")
            .should("have.text", "Choose Category")
            .and("be.visible");

        // Select a category
        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']").click({ force: true });

        // Assert that category select label changes and
        // URL is updated with selected category ID
        cy.get("div[data-testid='category-select']")
            .find(".v-select__selection")
            .should("have.text", "Related Statutes");
        cy.get("div[data-testid='category-select']")
            .find("label")
            .should("not.be.visible");
        cy.url().should("include", "/subjects?subjects=63&categories=3");

        // Select a different subject
        cy.get(`button[data-testid=add-subject-1]`).click({
            force: true,
        });

        // Assert that category is removed from URL and
        // category select label is reset
        cy.url().should("include", "/subjects?subjects=1");
        cy.url().should("not.include", "&categories=3");
        cy.get("div[data-testid='category-select']")
            .should("exist")
            .find("label")
            .should("have.text", "Choose Category")
            .and("be.visible");

        // Select a new category
        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']").click({ force: true });

        // Assert that category select label changes and URL updates
        cy.get("div[data-testid='category-select']")
            .find(".v-select__selection")
            .should("have.text", "Related Statutes");
        cy.get("div[data-testid='category-select']")
            .find("label")
            .should("not.be.visible");
        cy.url().should("include", "/subjects?subjects=1&categories=3");

        // Add text query and submit
        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        // Assert that category is removed from URL and
        // category select label is reset
        cy.url().should("include", "/subjects?subjects=1&q=test");
        cy.url().should("not.include", "&categories=3");
        cy.get("div[data-testid='category-select']")
            .should("exist")
            .find("label")
            .should("have.text", "Choose Category")
            .and("be.visible");
    });

    it("goes to another SPA page from the subjects page", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");
        cy.clickHeaderLink({
            page: "statutes",
            label: "Access Statute Citations",
            screen: "wide",
        });
        cy.url().should("include", "/statutes");
    });

    it("should have the correct labels for public and internal documents", () => {
        cy.checkPolicyDocs({
            username,
            password,
            landingPage: "/subjects/",
        });
    });

    it("should show the external only view of the subjects page after you log out", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");
        cy.eregsLogout({ landingPage: "/subjects" });
        cy.url().should("include", "/subjects");
        cy.get("button[data-testid='user-account-button']").should("not.exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("input")
            .should("be.checked")
            .and("be.disabled");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .should("not.be.checked")
            .and("be.disabled");
    });
});

describe("Subjects Page -- Pagination", () => {
    beforeEach(() => {
        _beforeEach();
        _beforePaginate();
    });

    it("Goes to the second page of results when clicking the Next button", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/" });
        cy.visit("/subjects");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .uncheck({ force: true });
        cy.get(".current-page.selected").contains("1");
        cy.get(".pagination-control.left-control > .back-btn").should(
            "have.class",
            "disabled"
        );
        cy.wait("@initialPage").then((interception) => {
            const count = interception.response.body.count;
            cy.get(".search-results-count").contains(
                `1 - 50 of ${count} documents`
            );
        });
        cy.get(".pagination-control.right-control")
            .contains("Next")
            .click({ force: true });
        cy.wait("@page2").then((interception) => {
            const count = interception.response.body.count;
            cy.url().should("include", "page=2");
            cy.get(".search-results-count").contains(
                `51 - 100 of ${count} documents`
            );
            cy.get(".current-page.selected").contains("2");
        });
    });

    it("Goes to the second page of results when clicking on page 2", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/" });
        cy.visit("/subjects");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .uncheck({ force: true });
        cy.get(".current-page.selected").contains("1");
        cy.get(".page-number-li.unselected")
            .contains("2")
            .click({ force: true });
        cy.wait("@page2").then((interception) => {
            const count = interception.response.body.count;
            cy.url().should("include", "page=2");
            cy.get(".search-results-count").contains(
                `51 - 100 of ${count} documents`
            );
            cy.get(".current-page.selected").contains("2");
        });
    });

    it("Goes to the second page of results on load when page=2 in the URL", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/" });
        cy.visit("/subjects/?type=external&page=2");
        cy.wait("@page2").then((interception) => {
            const count = interception.response.body.count;
            cy.get(".search-results-count").contains(
                `51 - 100 of ${count} documents`
            );
            cy.get(".current-page.selected").contains("2");
        });
    });
});

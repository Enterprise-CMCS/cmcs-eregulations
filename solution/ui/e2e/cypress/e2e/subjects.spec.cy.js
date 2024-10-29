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

    cy.intercept("**/v3/resources/subjects**", {
        fixture: "subjects.json",
    }).as("subjects");

    cy.intercept("**/v3/resources/internal/categories**", {
        fixture: "categories-internal.json",
    }).as("internalCategories");

    cy.intercept("**/v3/resources/public/categories**", {
        fixture: "categories.json",
    }).as("categories");
};

const _beforePaginate = () => {
    cy.intercept(
        "**/v3/resources/public?show_regulations=false&show_internal=false**",
        {
            fixture: "policy-docs-50-p1.json",
        }
    ).as("initialPage");

    cy.intercept("**/v3/resources/public?show_regulations=false&show_internal=false&page=1**", {
        fixture: "policy-docs-50-p1.json",
    }).as("page1");

    cy.intercept("**/v3/resources/public?show_regulations=false&show_internal=false&page=2**", {
        fixture: "policy-docs-50-p2.json",
    }).as("page2");
};

Cypress.Commands.add("getPolicyDocs", ({ username, password }) => {
    cy.intercept("**/v3/content-search/?q=mock**", {
        fixture: "policy-docs-search.json",
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
        cy.get(".doc-type__toggle fieldset").should("not.exist");

        cy.checkAccessibility();

        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] a"
        ).scrollIntoView();
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-3] div.subj-toc-li__count"
        )
            .should("be.visible")
            .and("have.text", "1 public resource");
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-63] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", "Managed Care")
            .click({ force: true });
        cy.get(".doc-type__toggle fieldset").should("not.exist");
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
            .and("have.text", "1 public and 0 internal resources");
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
            fixture: "policy-docs-search.json",
        });
        cy.intercept(
            "**/v3/resources/?&page_size=50&group_resources=false",
            {
                fixture: "policy-docs-subjects.json",
            }
        );
        cy.intercept(
            "**/v3/resources/?subjects=3&show_regulations=false&page_size=50&group_resources=false",
            {
                fixture: "policy-docs-subjects.json",
            }
        );
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
            "1 - 3 of 3 documents"
        );
        cy.get("input#main-content").type("mock", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });
        cy.get(".subject__heading").should("not.exist");
        cy.get(".search-results__heading")
            .should("exist")
            .and("have.text", " Search Results ");
        cy.get(".search-results-count").should(
            "have.text",
            "1 - 4 of 4 results for mock within Access to Services"
        );
        cy.get(`button[data-testid=remove-subject-3]`).click({
            force: true,
        });
        cy.get(".search-results-count").should(
            "have.text",
            "1 - 4 of 4 results for mock"
        );
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
            .and("include", "/42/440/130#440-130");
        cy.get(".result__link") // internal_file
            .eq(0)
            .should("include.text", "Download")
            .find("a")
            .should("not.have.class", "external")
            .find(
                "span[data-testid=download-chip-868e968c-d1f5-4518-b458-b6e735ef0f3d]"
            )
            .should("include.text", "Download MSG");
        cy.get(".result__link") // regulations link
            .eq(1)
            .find("a")
            .should("not.include.text", "Download")
        cy.get(".result__link") // internal_link
            .eq(2)
            .find("a")
            .should("not.include.text", "Download")
            .and("have.class", "external");
        cy.get(".doc-type__label")
            .eq(0)
            .should("include.text", " Internal")
            .find("i")
            .should("have.class", "fa-key");
        cy.get(".doc-type__label")
            .eq(1)
            .should("include.text", " Public")
            .find("i")
            .should("have.class", "fa-users");

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
            fixture: "policy-docs-search.json",
        }).as("subjectFiles");
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });

        cy.visit("/subjects/");
        cy.get(`button[data-testid=add-subject-3]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=3");
        cy.get("input#main-content")
            .should("be.visible")
            .type("test search", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });
        cy.url().should(
            "include",
            "/subjects?subjects=3&q=test+search"
        );
        cy.get(".search-form .form-helper-text .search-suggestion").should(
            "not.exist"
        );
        cy.get(".document__subjects a")
            .eq(0)
            .should("have.text", "FMAP");
        cy.get(".document__subjects a")
            .eq(1)
            .should("have.text", "Preventive Services");
        cy.get(".document__subjects a")
            .eq(2)
            .should("have.text", "VIII group");
        cy.get(`a[data-testid=add-subject-chip-167]`)
            .should("have.attr", "title")
            .and("include", "New Adult Group");
        cy.get(`a[data-testid=add-subject-chip-167]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=167");
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

    it("should have a Documents to Show checkbox list only when a subject is selected or text is searched", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");

        // doc type checkboxes should not be visible on load
        cy.get(".doc-type__toggle fieldset").should("not.exist");

        // select a subject fro ToC
        cy.get(
            ".subj-toc__list li[data-testid=subject-toc-li-63] a"
        ).scrollIntoView();
        cy.get(".subj-toc__list li[data-testid=subject-toc-li-63] a")
            .should("have.text", "Managed Care")
            .click({ force: true });

        // doc type checkboxes should be visible now
        cy.get(".doc-type__toggle fieldset > div").should("have.length", 2);
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("label")
            .should("have.text", "Public Resources");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("label")
            .should("have.text", "Internal Resources");

        // Remove subject
        cy.get("button[data-testid=remove-subject-63]").click({ force: true });

        // doc type checkboxes should no longer be visible
        cy.get(".doc-type__toggle fieldset").should("not.exist");

        // search for a term
        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        // doc type checkboxes should be visible now
        cy.get(".doc-type__toggle fieldset > div").should("have.length", 2);
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("label")
            .should("have.text", "Public Resources");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("label")
            .should("have.text", "Internal Resources");

        // Clear search
        cy.get("form.search-form .v-field__clearable i").click({
            force: true,
        });

        // doc type checkboxes should no longer be visible
        cy.get(".doc-type__toggle fieldset").should("not.exist");
    });

    it("should show only the Table of Contents if both or neither checkboxes are checked", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects?type=internal");
        cy.get(".subj-toc__container").should("not.exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .uncheck({ force: true });
        cy.get(".subj-toc__container").should("exist");
        cy.get(".doc-type__toggle fieldset").should("not.exist");
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
            .should("have.text", "Related Regulations Fixture Item");
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
            .should("have.text", "Related Statutes in Fixture");
        cy.get("div[data-testid='category-select']")
            .find("label")
            .should("not.be.visible");

        // Assert that External document type checkbox has been selected
        // and Internal document type checkbox has been deselected
        cy.get(".doc-type__toggle fieldset")
            .eq(0)
            .find("input")
            .should("be.checked");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .should("not.be.checked");

        cy.url().should(
            "include",
            "/subjects?subjects=63&categories=1&type=external"
        );

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
            .should("have.text", "Related Statutes in Fixture");
        cy.get("div[data-testid='category-select']")
            .find("label")
            .should("not.be.visible");
        cy.url().should(
            "include",
            "/subjects?subjects=1&categories=1&type=external"
        );

        // Add text query and submit
        cy.get("input#main-content")
            .should("be.visible")
            .type("test", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        // Assert that category is removed from URL and
        // category select label is reset
        cy.url().should("include", "/subjects?subjects=1&type=external&q=test");
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

    it("should not show document type selector after you log out", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");

        cy.get(`button[data-testid=add-subject-1]`).click({
            force: true,
        });
        cy.get(".doc-type__toggle fieldset").should("exist");

        cy.eregsLogout({ landingPage: "/subjects" });
        cy.url().should("include", "/subjects");
        cy.get("button[data-testid='user-account-button']").should("not.exist");
        cy.get(".doc-type__toggle fieldset").should("not.exist");
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
        cy.visit("/subjects?type=external");
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
        cy.visit("/subjects?type=external");
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

    it("Goes to the second page of results on load when page=2 AND a category in the URL", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password, landingPage: "/" });
        cy.visit("/subjects/?type=external&page=2&categories=3");
        cy.wait("@page2").then((interception) => {
            const count = interception.response.body.count;
            cy.get(".search-results-count").contains(
                `51 - 100 of ${count} documents`
            );
            cy.get(".current-page.selected").contains("2");
            cy.url().should(
                "include",
                "/subjects/?type=external&page=2&categories=3"
            );
        });
    });
});

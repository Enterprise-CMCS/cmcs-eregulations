const TITLE_42 = 42;
const TITLE_45 = 45;

const username = Cypress.env("TEST_USERNAME");
const password = Cypress.env("TEST_PASSWORD");
const readerUsername = Cypress.env("READER_USERNAME");
const readerPassword = Cypress.env("READER_PASSWORD");

const _beforeEach = () => {
    cy.env(["DEPLOYING"]).then(({ DEPLOYING }) => {
        cy.intercept("/**", (req) => {
            req.headers["x-automated-test"] = DEPLOYING;
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
    });
};

const _beforePaginate = () => {
    cy.intercept(
        "**/v3/resources/public?show_regulations=false&show_internal=false**",
        {
            fixture: "policy-docs-50-p1.json",
        },
    ).as("initialPage");

    cy.intercept(
        "**/v3/resources/public?show_regulations=false&show_internal=false&page=1**",
        {
            fixture: "policy-docs-50-p1.json",
        },
    ).as("page1");

    cy.intercept(
        "**/v3/resources/public?show_regulations=false&show_internal=false&page=2**",
        {
            fixture: "policy-docs-50-p2.json",
        },
    ).as("page2");
};

Cypress.Commands.add("getPolicyDocs", ({ username, password }) => {
    cy.intercept("**/v3/resources/?subjects=3**", {
        fixture: "policy-docs-search.json",
    }).as("subjectFiles");
    cy.viewport("macbook-15");
    cy.eregsLogin({ username, password, landingPage: "/subjects/" });
    cy.visit("/subjects/?subjects=3");
    cy.injectAxe();
    cy.wait("@subjectFiles").then((interception) => {
        expect(interception.response.statusCode).to.eq(200);
    });
});

describe("Find by Subjects", () => {
    beforeEach(_beforeEach);

    it("redirects /policy-repository to /subjects", () => {
        cy.viewport("macbook-15");
        cy.visit("/policy-repository?subjects=2");
        cy.url().should("not.include", "/policy-repository");
        cy.url().should("include", "/subjects/").and("include", "subjects=2");
    });

    it("redirects /resources to /subjects", () => {
        cy.viewport("macbook-15");
        cy.visit("/resources?q=test");
        cy.url().should("not.include", "/resources");
        cy.url().should("include", "/subjects/").and("not.include", "q=test");
    });

    it("strips the q parameter out of the URL if it is included in the URL on load", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/?subjects=2&q=test");
        cy.url()
            .should("include", "/subjects?subjects=2")
            .and("not.include", "q=test");
    });

    it("shows the sign in Call to Action on landing page when not logged in and no subjects are selected", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects", { timeout: 60000 });
        cy.get(
            ".subject__filters--row .login-cta__div--subjects-results",
        ).should("not.exist");
        cy.get(".subj-landing__container .login-cta__div").contains(
            "To see internal documents, sign in or learn how to get account access.",
        );
        cy.get("span[data-testid=loginSubjectsLanding] a")
            .should("have.attr", "href")
            .and("include", "/login/?next=")
            .and("include", "/subjects/");
        cy.get("a.access__anchor")
            .should("have.attr", "href")
            .and("include", "/get-account-access/");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/search/",
        });
        cy.visit("/subjects");
        cy.get(".subj-landing__container .login-cta__div").should("not.exist");
    });

    it("shows the sign in Call to Action when not logged in and a subject is selected", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects?subjects=77");
        cy.get(".subj-landing__container .login-cta__div").should("not.exist");
        cy.get(".subject__filters--row .login-cta__div--subjects-results").contains(
            "To see internal documents, sign in or learn how to get account access.",
        );
        cy.get("span[data-testid=loginSubjectsResults] a")
            .should("have.attr", "href")
            .and("include", "/login/?next=")
            .and("include", "/subjects/?subjects=77");
        cy.get("a.access__anchor")
            .should("have.attr", "href")
            .and("include", "/get-account-access/");

        cy.eregsLogin({
            username,
            password,
            landingPage: "/search/",
        });
        cy.visit("/subjects?subjects=77");
        cy.get(".subject__filters--row .login-cta__div--subjects-results").should("not.exist");
    });

    it("should show only public items when logged out", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/");

        cy.injectAxe();

        cy.get("button[data-testid='user-account-button']").should("not.exist");
        cy.get(".doc-type__toggle fieldset").should("not.exist");

        cy.checkAccessibility();

        cy.get(".subjects__list button[data-testid=add-subject-3] span.count:not(:hidden)")
            .should("be.visible")
            .and("have.text", "(1)");
        cy.get(
            ".subjects__list button[data-testid=add-subject-63]",
        ).scrollIntoView();
        cy.get(".subjects__list button[data-testid=add-subject-63]")
            .should("have.text", "Managed Care")
            .click({ force: true });
        cy.get(".doc-type__toggle fieldset").should("not.exist");
        cy.get(".subject__heading h1")
            .should("exist")
            .and("have.text", "Managed Care");
        cy.get("span[data-testid=selected-subject-description]")
            .should("have.text", "Managed Care Description")
        cy.url().should("include", "/subjects?subjects=63");
    });

    it("should strip document-type query parameter from URL when not logged in", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects/?type=internal");
        cy.url().should("not.include", "type");
    });

    it("should redirect to the Search page with the correct selected subject and filters when a search term is entered", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/subjects");

        // Select a subject
        cy.get(".subjects__list button[data-testid=add-subject-3]")
            .should("have.text", "Access to Services(1)")
            .click({ force: true });

        // Select a category and document type
        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']").click({ force: true });

        // Search for a term
        cy.get("input#main-content").type("mock", { force: true });
        cy.get('[data-testid="search-form-submit"]').click({
            force: true,
        });

        // Assert URL
        cy.url()
            .should("include", "/search")
            .and("include", "q=mock")
            .and("include", "type=external")
            .and("include", "subjects=3")
            .and("include", "categories=1");
    });

    it("clearing the search input should not reload the page", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/subjects");

        // select subject
        cy.get(".subjects__list button[data-testid=add-subject-3]")
            .should("have.text", "Access to Services(1)")
            .click({ force: true });

        // select category
        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']").click({ force: true });

        cy.url().should(
            "include",
            "/subjects?subjects=3&categories=1&type=external",
        );

        cy.get("input#main-content").should("have.value", "");

        cy.get("input#main-content").type("mock", { force: true });

        cy.get("input#main-content").should("have.value", "mock");

        cy.get(".search-field")
            .find(".v-field__clearable i")
            .should("have.attr", "title")
            .and("include", "Clear All");

        cy.get(".search-field")
            .find(".v-field__clearable i")
            .click({ force: true });

        cy.get("input#main-content").should("have.value", "");

        cy.url().should(
            "include",
            "/subjects?subjects=3&categories=1&type=external",
        );
    });

    it("should display the appropriate results column header when viewing the items within a subject.", () => {
        cy.intercept("**/v3/resources/?&page_size=50&group_resources=false", {
            fixture: "policy-docs-subjects.json",
        });
        cy.intercept(
            "**/v3/resources/?subjects=3&show_regulations=false&page_size=50&group_resources=false",
            {
                fixture: "policy-docs-subjects.json",
            },
        );
        cy.viewport("macbook-15");
        cy.eregsLogin({ username, password });
        cy.visit("/subjects");
        cy.get(".subjects__list button[data-testid=add-subject-3]")
            .should("have.text", "Access to Services(1)")
            .click({ force: true });
        cy.url().should("include", "/subjects?subjects=3");
        cy.get(".subject__heading h1")
            .should("exist")
            .and("have.text", "Access to Services");
        cy.get("span[data-testid=selected-subject-description]")
            .should("have.text", "Access to Services Description")
        cy.get("search-results__heading").should("not.exist");
        cy.get(".search-results-count").should(
            "have.text",
            "1 - 3 of 3 documents",
        );
    });

    it("loads the correct subject when the URL is changed", () => {
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
        cy.get(".subject__heading h1 span")
            .eq(0)
            .should("have.text", "Cures Act")
            .and("have.class", "subj-heading__span--bold");
        cy.get(".subject__heading h1 span")
            .eq(1)
            .should("have.text", "21st Century Cures Act")
            .and("not.have.class", "subj-heading__span--bold");
        cy.get("span[data-testid=selected-subject-description]")
            .should("have.text", "Cures Act Description")

        cy.get(`button[data-testid=add-subject-2]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=2");
        cy.get(`button[data-testid=remove-subject-2]`).should("exist");
        cy.get(".subject__heading h1 span")
            .eq(0)
            .should("have.text", "ABP")
            .and("have.class", "subj-heading__span--bold");
        cy.get(".subject__heading h1 span")
            .eq(1)
            .should("have.text", "Alternative Benefit Plan")
            .and("not.have.class", "subj-heading__span--bold");
        cy.get("span[data-testid=selected-subject-description]")
            .should("not.exist");

        cy.get(`button[data-testid=add-subject-3]`).click({
            force: true,
        });
        cy.url().should("include", "/subjects?subjects=3");
        cy.get(`button[data-testid=remove-subject-3]`).should("exist");
        cy.get(".subject__heading h1 span")
            .eq(0)
            .should("have.text", "Access to Services")
            .and("have.class", "subj-heading__span--bold");
        cy.get(".subject__heading h1 span").eq(1).should("not.exist");
        cy.get("span[data-testid=selected-subject-description]")
            .should("have.text", "Access to Services Description")

        cy.go("back");
        cy.url().should("include", "/subjects?subjects=2");
        cy.get(`button[data-testid=remove-subject-3]`).should("not.exist");
    });

    it("should display the correct related statutes and regulations", () => {
        cy.getPolicyDocs({ username, password });
        // check related statute without url
        cy.get(".related-statutes")
            .first()
            .find(".related-section-item")
            .first()
            .find(".related-statute__span")
            .should("have.text", "1905(r)")
            .and("not.have.attr", "href");
        // check related statute with url
        cy.get(".related-statutes")
            .first()
            .find(".related-section-item")
            .eq(1)
            .find("a.related-statute__link")
            .first()
            .should("have.text", "6409")
            .and("have.attr", "href")
            .and("include", "https://www.mock-url.com");
        // check related regulation
        cy.get(".related-regulations")
            .first()
            .find(".related-section-item")
            .first()
            .find("a")
            .should("have.attr", "href")
            .and("not.include", "undefined")
            .and("include", "/42/440/130#440-130");
    });

    it("should display and fetch the correct subjects on load if they are included in URL", () => {
        cy.getPolicyDocs({ username, password });
        cy.get(".result__link") // internal_file
            .eq(0)
            .find("a")
            .should("not.have.class", "external")
            .find(
                "span[data-testid=download-chip-868e968c-d1f5-4518-b458-b6e735ef0f3d]",
            )
            .should("include.text", "Outlook");
        cy.get(".result__link") // internal_file
            .eq(0)
            .find("a")
            .find("span.result__link--domain")
            .should("not.exist");
        cy.get(".result__link") // regulations link
            .eq(1)
            .find("a")
            .find("span.result__link--file-type")
            .should("include.text", "PDF");
        cy.get(".result__link") // regulations link
            .eq(1)
            .find("a")
            .find("span.result__link--domain")
            .should("include.text", "medicaid.gov");
        cy.get(".result__link") // internal_link
            .eq(2)
            .find("a")
            .should("not.have.class", "external")
            .find("span.result__link--file-type")
            .should("include.text", "DOCX");
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
        cy.intercept("**/v3/resources/?subjects=3**", {
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
        cy.get(".document__subjects a").eq(0).should("have.text", "FMAP");
        cy.get(".document__subjects a")
            .eq(1)
            .should("have.text", "Preventive Services");
        cy.get(".document__subjects a").eq(2).should("have.text", "VIII group");
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
            "subjects-li__button--selected",
        );
        cy.get("button[data-testid=add-subject-63]").click({
            force: true,
        });
        cy.get("button[data-testid=add-subject-63]").should("not.exist");
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
            "Cures Act",
        );
        cy.get(`button[data-testid=clear-subject-filter]`).should(
            "not.be.visible",
        );

        cy.checkAccessibility();

        cy.get("input#subjectReduce")
            .should("exist")
            .and("have.value", "")
            .and("have.attr", "placeholder", "Find a subject")
            .type("21", { force: true });
        cy.get(`button[data-testid=clear-subject-filter]`).should("exist");
        cy.get("input#subjectReduce").should("have.value", "21");
        cy.get(".subjects__list li").should("have.length", 1);
        cy.get(`button[data-testid=add-subject-1]`)
            .should("include.text", "21st Century Cures Act")
            .find("span.count:not(:hidden)")
            .should("include.text", "(1)");
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
        cy.get(".subjects__list li").should("have.length", 77);
    });

    it("should not add bold styling to Subject Selector list item when focused", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects");
        cy.get(".subjects__list .subjects__li button").first().focus();
        cy.focused()
            .find(".subjects-li__button-subtitle")
            .should("have.css", "font-weight", "400");
    });

    it("should have a Documents to Show checkbox list only when a subject or category is selected", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects");

        // doc type checkboxes should not be visible on load
        cy.get(".doc-type__toggle fieldset").should("not.exist");

        // select a subject from ToC
        cy.get(".subjects__list button[data-testid=add-subject-63]")
            .should("have.text", "Managed Care")
            .click({ force: true });

        // doc type checkboxes should be visible now
        cy.get(".doc-type__toggle fieldset > div").should("have.length", 2);
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("label")
            .should("include.text", "Public Resources");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("label")
            .should("include.text", "Internal Resources");

        // Remove subject
        cy.get("button[data-testid=remove-subject-63]").click({ force: true });

        // doc type checkboxes should no longer be visible
        cy.get(".doc-type__toggle fieldset").should("not.exist");

        // select a subject from ToC once again
        cy.get(".subjects__list button[data-testid=add-subject-63]")
            .should("have.text", "Managed Care")
            .click({ force: true });

        // doc type checkboxes should be visible now
        cy.get(".doc-type__toggle fieldset > div").should("have.length", 2);
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("label")
            .should("include.text", "Public Resources");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("label")
            .should("include.text", "Internal Resources");

        // Select a category
        cy.get("div[data-testid='category-select']").click();
        cy.get("div[data-testid='external-0']").click({ force: true });

        // remove subject
        cy.get("button[data-testid=remove-subject-63]").click({ force: true });

        // doc type checkboxes should still be visible
        cy.get(".doc-type__toggle fieldset > div").should("have.length", 2);
        cy.get(".doc-type__toggle fieldset > div")
            .eq(0)
            .find("label")
            .should("include.text", "Public Resources");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("label")
            .should("include.text", "Internal Resources");
    });

    it("should show only the Landing Page if both or neither checkboxes are checked", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects?type=internal");
        cy.get(".subj-landing__container").should("not.exist");
        cy.get(".doc-type__toggle fieldset > div")
            .eq(1)
            .find("input")
            .uncheck({ force: true });
        cy.get(".subj-landing__container")
            .should("exist")
            .find("h1")
            .should("have.text", "Find Policy Documents");
        cy.get(".doc-type__toggle fieldset").should("not.exist");
        cy.url().should("include", "/subjects");
    });

    it("should clear URL params and show the Landing Page when the Research a Subject header link is clicked", () => {
        cy.viewport("macbook-15");
        cy.eregsLogin({
            username,
            password,
            landingPage: "/subjects/",
        });
        cy.visit("/subjects?type=internal");
        cy.get(".subj-landing__container").should("not.exist");
        cy.get(
            `header .header--links .links--container > ul.links__list li a[data-testid=subjects]`,
        ).click({ force: true });
        cy.get(".subj-landing__container").should("exist");
    });

    it("should have a link to the About page in the Landing message", () => {
        cy.viewport("macbook-15");
        cy.visit("/subjects");
        cy.get(".subj-landing__container a.about__anchor")
            .should("have.text", "Learn more about documents on eRegs.")
            .and("have.attr", "href")
            .and("include", "/about");
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
        cy.visit("/subjects?subjects=3");

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
        cy.visit("/subjects?subjects=3");

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
        cy.get(".subjects__list button[data-testid=add-subject-63]")
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

    it("should clear selected category if subject is toggled", () => {
        cy.viewport("macbook-15");

        // Log in
        cy.eregsLogin({ username, password, landingPage: "/subjects/" });
        cy.visit("/subjects/");

        // Assert that category filter is not visible
        cy.get("div[data-testid='category-select']").should("not.exist");

        // Select a subject
        cy.get(".subjects__list button[data-testid=add-subject-63]")
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
            "/subjects?subjects=63&categories=1&type=external",
        );

        // Select a different subject
        cy.get(`button[data-testid=add-subject-1]`).click({
            force: true,
        });

        // Assert that category is removed from URL and
        // category select label remains the same
        cy.url().should("include", "/subjects?subjects=1")
            .and("not.include", "&categories=1");
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
            "/subjects?subjects=1&categories=1",
        );
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
            label: "Social Security Act",
            screen: "wide",
        });
        cy.url().should("include", "/statutes");
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
            "disabled",
        );
        cy.wait("@initialPage").then((interception) => {
            const count = interception.response.body.count;
            cy.get(".search-results-count").contains(
                `1 - 50 of ${count} documents`,
            );
        });
        cy.get(".pagination-control.right-control")
            .contains("Next")
            .click({ force: true });
        cy.wait("@page2").then((interception) => {
            const count = interception.response.body.count;
            cy.url().should("include", "page=2");
            cy.get(".search-results-count").contains(
                `51 - 100 of ${count} documents`,
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
                `51 - 100 of ${count} documents`,
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
                `51 - 100 of ${count} documents`,
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
                `51 - 100 of ${count} documents`,
            );
            cy.get(".current-page.selected").contains("2");
            cy.url().should(
                "include",
                "/subjects/?type=external&page=2&categories=3",
            );
        });
    });
});

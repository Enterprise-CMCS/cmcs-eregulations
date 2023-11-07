// login via policy repository page for now
export const eregsLogin = ({
    username,
    password,
    landingPage = "/policy-repository/",
}) => {
    cy.session([username, password, landingPage], () => {
        cy.visit(landingPage);
        cy.wait(1000);
        cy.get("#id_username").type(username);
        cy.get("#id_password").type(password);
        cy.get("#login-form").submit();
    });
};
export const setUserGroup = () => {
    cy.intercept('GET', '**/api/user-group-endpoint').as('getUserGroups');

    // Make a request to fetch the user's group membership
    cy.route('GET', '**/api/user-group-endpoint').as('getUserGroups');

    // Visit a page that requires the user's group data (adjust the URL accordingly)
    cy.visit('/some-page-that-requires-group-info');

    // Wait for the user's group data to be fetched
    cy.wait('@getUserGroups').then((interception) => {
        // Access the response data (contains user's group membership)
        const userGroups = interception.response.body;

        // Check if the user is part of EREGS_EDITOR and any other EREGS_ group
        const isEREGSEditor = userGroups.includes('EREGS_EDITOR');
        const isOtherEREGSGroup = userGroups.some(group => group.startsWith('EREGS_') && group !== 'EREGS_EDITOR');

        // Set a flag to indicate whether the user has an editable job code
        const hasEditableJobCode = isEREGSEditor ? false : isOtherEREGSGroup;

        // Store this information for later use (for example, in Cypress environment variables)
        Cypress.env('hasEditableJobCode', hasEditableJobCode);
    });
};
// login via policy repository page for now
export const eregsLogin = ({ username, password, landingPage = "/" }) => {
    const cypressAdminToken = Cypress.env("ADMIN_LOGIN_TOKEN");
    if (!cypressAdminToken) {
        throw new Error("ADMIN_LOGIN_TOKEN is not available to Cypress");
    }
    cy.visit("/admin/login/", {
        headers: cypressAdminToken
            ? { "X-eRegs-Cypress-Admin-Token": cypressAdminToken }
            : {},
    });
    cy.get("#id_username").type(username);
    cy.get("#id_password").type(password);
    cy.get("#login-form").submit();
    cy.visit(landingPage);
};

export const eregsLogout = ({ landingPage = "/" }) => {
    cy.get("button[data-testid='user-account-button']").click();
    cy.get("form#oidc_logout").submit();
    cy.visit(landingPage);
};

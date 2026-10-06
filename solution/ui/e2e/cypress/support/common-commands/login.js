// login via policy repository page for now
export const eregsLogin = ({ username, password, landingPage = "/" }) => {
    cy.env(["ADMIN_LOGIN_TOKEN"]).then(({ ADMIN_LOGIN_TOKEN }) => {
        cy.visit("/admin/login/", {
            headers: ADMIN_LOGIN_TOKEN
                ? { "X-eRegs-Cypress-Admin-Token": ADMIN_LOGIN_TOKEN }
                : {},
        });
        cy.get("#id_username").type(username);
        cy.get("#id_password").type(password);
        cy.get("#login-form").submit();
        cy.visit(landingPage);
    });
};

export const eregsLogout = ({ landingPage = "/" }) => {
    cy.get("button[data-testid='user-account-button']").click();
    cy.get("form#oidc_logout").submit();
    cy.visit(landingPage);
};

// login via policy repository page for now
export const eregsLogin = ({ username, password, landingPage = "/" }) => {
    cy.visit("/admin");
    cy.wait(1000);
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

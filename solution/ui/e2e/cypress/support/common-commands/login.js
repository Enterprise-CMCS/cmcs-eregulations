export const adminLogin = ({ username, password }) => {
    cy.session([username, password], () => {
        cy.visit("/admin");
        cy.get("#id_username").type(username);
        cy.get("#id_password").type(password);
        cy.get("#login-form").submit();
    });
};

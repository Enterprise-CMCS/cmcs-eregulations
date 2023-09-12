// login via policy repository page for now
export const eregsLogin = ({ username, password }) => {
    cy.session([username, password], () => {
        cy.visit("/policy-repository/");
        cy.get("#id_username").type(username);
        cy.get("#id_password").type(password);
        cy.get("#login-form").submit();
    });
};

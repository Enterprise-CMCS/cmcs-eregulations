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


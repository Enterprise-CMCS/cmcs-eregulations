describe('Admin login via EUA Test', () => {
  beforeEach(() => {
    cy.visit('/admin/login/');
  });

  it('should display EUA content when EUA_FEATUREFLAG is true', () => {
    // Set the EUA_FEATUREFLAG environment variable to True
    cy.exec('export EUA_FEATUREFLAG=true');

    // Reload the page to apply the feature flag
    cy.reload();
    cy.get('.okta_login_container').should('exist');
    cy.contains('Or Login With EUA').should('exist');
  });

  it('should not display EUA content when EUA_FEATUREFLAG is False', () => {
    // Set the EUA_FEATUREFLAG environment variable to False
    cy.exec('export EUA_FEATUREFLAG=false');

    // Reload the page to apply the feature flag
    cy.reload();

    // Assert that the EUA login link is not displayed
    cy.get('.okta_login_container').should('not.exist');
    cy.contains('Or Login With EUA').should('not.exist');
  });
});

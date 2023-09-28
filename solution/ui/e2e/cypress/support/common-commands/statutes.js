export const clickStatuteLink = ({ act, title, titleRoman }) => {
    cy.get(`a[data-testid=${act}-${titleRoman}-${title}]`).click({
        force: true,
    });
};

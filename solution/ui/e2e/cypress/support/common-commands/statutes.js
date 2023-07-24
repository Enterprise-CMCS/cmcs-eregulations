export const clickStatuteLink = ({ act, title, titleRoman }) => {
    const testId = `ssa-${titleRoman}-${title}`;
    cy.get(`a[data-testid=${act}-${titleRoman}-${title}]`).click({
        force: true,
    });
};

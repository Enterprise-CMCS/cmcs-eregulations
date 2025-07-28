export const clickStatuteTab = ({ act, title, titleRoman }) => {
    cy.get(`button[data-testid=${act}-${titleRoman}-${title}]`).click({
        force: true,
    });
};

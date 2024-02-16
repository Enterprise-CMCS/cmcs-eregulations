export const getResources = (q, page = 1) => {
    cy.request({
        url: `v3/resources/`,
        method: "GET",
        qs: {
            q,
            page,
            "category_details": "true",
            "location_details": "true",
        },
    });
};

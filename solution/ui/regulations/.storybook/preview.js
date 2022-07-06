import "!style-loader!raw-loader!../../../static-assets/regulations/css/main.css";

export const parameters = {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: { expanded: true },
    options: {
        storySort: {
            order: [
                "Regulations",
                "Prototype",
                "Supplemental Resources",
                "Components",
            ],
        },
    },
};

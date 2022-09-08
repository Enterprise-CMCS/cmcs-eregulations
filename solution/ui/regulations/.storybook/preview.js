import { initialize, mswDecorator } from "msw-storybook-addon";
import { rest } from 'msw'
import "!style-loader!raw-loader!../../../static-assets/regulations/css/main.css";

import toc from "mocks/toc"

// Initialize MSW
initialize();

// Provide the MSW addon decorator globally
export const decorators = [mswDecorator];

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
    msw: {
        handlers: {
            others: [
                rest.get(
                    "*/v3/title/42/part/433/version/latest/subpart/A/toc",
                    (req, res, ctx) => {
                        return res(
                            ctx.status(200),
                            ctx.json(toc)
                        );
                    }
                ),
            ],
        },
    },
};

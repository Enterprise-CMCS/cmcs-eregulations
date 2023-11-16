import { initialize, mswDecorator } from "msw-storybook-addon";
import { rest } from 'msw'
import "!style-loader!raw-loader!../../../static-assets/regulations/css/main.css";

import toc from "mocks/toc";
import { locations } from "mocks/locations";

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
                "Supplemental Resources",
                "Components",
            ],
        },
    },
    msw: {
        handlers: {
            toc: [
                rest.get(
                    "*/v3/title/:title/part/:part/version/:version/subpart/:subpart/toc",
                    (req, res, ctx) => {
                        return res(
                            ctx.status(200),
                            ctx.json(toc[req.params.part])
                        );
                    }
                ),
            ],
        },
    },
};

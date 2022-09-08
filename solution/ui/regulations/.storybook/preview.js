import { initialize, mswDecorator } from "msw-storybook-addon";
import { rest } from 'msw'
import "!style-loader!raw-loader!../../../static-assets/regulations/css/main.css";

import toc from "mocks/toc";
import locations from "mocks/locations";

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
                rest.get(
                    "*/v3/resources/?locations=42.433.8&locations=42.433.10&locations=42.433.11&locations=42.433.15&locations=42.433.32&locations=42.433.34&locations=42.433.35&locations=42.433.36&locations=42.433.37&locations=42.433.38&locations=42.433.40&locations=42.433.A&paginate=true&location_details=false",
                    (req, res, ctx) => {
                        return res(
                            ctx.status(200),
                            ctx.json(locations)
                        );
                    }
                ),
            ],
        },
    },
};

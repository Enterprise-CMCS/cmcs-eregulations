import { rest } from "msw";
import { partToc42, partToc45 } from "./part_toc.js";
import { titles } from "./titles.js";
import { subpartResources, sectionResources } from "./resources.js";
import { subpartA } from "./subpartTOC.js";
import { titleFourtyTwoSuccess } from "./parser_success.js";
import { history } from "./govInfoHistory.js";

const handlers = [
    rest.get("*/title/42/parts", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(partToc42))
    ),
    rest.get("*/title/45/parts", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(partToc45))
    ),
    rest.get("*/titles", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(titles))
    ),
    rest.get(
        "*/title/42/part/433/version/latest/subpart/A/toc",
        (req, res, ctx) => res(ctx.status(200), ctx.json(subpartA))
    ),
    rest.get("*/resources/", (req, res, ctx) => {
        const locations = req.url.searchParams.getAll("locations");
        if (locations[0] === "42.433.10") {
            return res(ctx.status(200), ctx.json(sectionResources));
        }
        return res(ctx.status(200), ctx.json(subpartResources));
    }),
    rest.get("*/ecfr_parser_result/42", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(titleFourtyTwoSuccess))
    ),
    rest.get("*/title/42/part/431/history/section/10", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(history))
    ),
];
export default handlers;

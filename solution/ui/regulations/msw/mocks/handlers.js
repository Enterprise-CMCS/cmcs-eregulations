import { rest } from "msw";
import { partToc42, partToc45 } from "./part_toc.js";
import { titles } from "./titles.js";

const handlers = [
    rest.get("*/title/42/parts", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(partToc42))
    ),
    rest.get("*/title/45/parts", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(partToc45))
    ),
    rest.get("*/titles", (req, res, ctx) =>
        res(ctx.status(200), ctx.json(titles))
    )
];
export default handlers;

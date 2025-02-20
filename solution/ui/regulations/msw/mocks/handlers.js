import { http, HttpResponse } from "msw";
import { partToc42, partToc45 } from "./part_toc.js";
import { titles } from "./titles.js";
import { subpartResources } from "./resources.js";
import { subpartA } from "./subpartTOC.js";
import { noEndCondition, titleFourtyTwoSuccess } from "./parser_success.js";
import { history } from "./govInfoHistory.js";

const handlers = [
    http.get("*/title/42/parts", () => {
        return HttpResponse.json(partToc42);
    }),
    http.get("*/title/45/parts", () => {
        return HttpResponse.json(partToc45);
    }),
    http.get("*/titles", () => {
        return HttpResponse.json(titles);
    }),
    http.get("*/title/42/part/433/version/latest/subpart/A/toc", () => {
        return HttpResponse.json(subpartA);
    }),
    http.get("*/resources/", () => {
        return HttpResponse.json(subpartResources);
    }),
    http.get("**test/success/ecfr_parser_result/42", () => {
        return HttpResponse.json(titleFourtyTwoSuccess);
    }),
    http.get("**/test/n/a/ecfr_parser_result/42", () => {
        return HttpResponse.json(noEndCondition);
    }),
    http.get("*/title/42/part/431/history/section/10", () => {
        return HttpResponse.json(history);
    }),
];
export default handlers;

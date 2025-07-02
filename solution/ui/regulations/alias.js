import { resolve } from "path";

const r = (p) => resolve(__dirname, p);

export default {
    "@": r("src"),
    composables: r("./composables"),
    cypress: r("../e2e/cypress"),
    eregsComponentLib: r("../regulations/eregs-component-lib"),
    legacy: r("../../regulations"),
    sharedComponents: r(
        "../regulations/eregs-component-lib/src/components/shared-components"
    ),
    spaComponents: r("../regulations/eregs-vite/src/components"),
    utilities: r("./utilities"),
    vite: r("../regulations/eregs-vite/src"),
};

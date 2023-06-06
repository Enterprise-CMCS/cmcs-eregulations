import {resolve} from 'path'

const r = (p) => resolve(__dirname, p)

export const aliases = {
    "utilities": r('./utilities'),
    "legacy": r("../../regulations"),
    "sharedComponents": r("../eregs-component-lib/src/components/shared-components"),
    "eregsComponentLib": r("../eregs-component-lib"),
    "vite": r("../regulations/eregs-vite/src"),
    "@": r("src"),
  }


import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import globalConfig from "../eslint-global-rules.mjs";

export default [
    { files: ["**/*.{js,mjs,cjs,ts}"] },
    { languageOptions: { globals: globals.browser } },
    pluginJs.configs.recommended,
    ...tseslint.configs.recommended,
    {
        rules: {
            ...globalConfig,
        },
    },
];

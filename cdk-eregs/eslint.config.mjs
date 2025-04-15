import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import globalConfig from "../eslint-global-rules.mjs";

export default [
    { files: ["**/*.{js,mjs,cjs,ts}"] },
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node
            }
        }
    },
    ...tseslint.configs.recommended,
    {
        files: ["**/*.js", "**/*.mjs", "**/*.cjs", "**/*.ts"],
        rules: {
            ...pluginJs.configs.recommended.rules,
            "indent": ["error", 4, { SwitchCase: 1 }],
        }
    },
    {
        rules: {
            ...globalConfig,
        },
    }
];

---
inject: true
to: ui/regulations/rollup.config.js
after: "#### HYGEN INSERTION POINT DO NOT REMOVE ####"
---
    {
        input: "js/src/components/<%= name %>Component.vue",
        output: {
            format: "esm",
            file: "dist/<%= name %>Component.js",
        },
        plugins,
    },
import vue from 'rollup-plugin-vue'

export default [
    {
        // ...
        input: 'components/RelatedRules.vue',
        output: {
            format: 'esm',
            file: 'regulations/js/RelatedRules.js'
        },
        plugins: [
            // ...
            vue(/* options */)
        ]
    },
    {
        input: 'components/CollapseButton.vue',
        output: {
            format: 'esm',
            file: 'regulations/js/CollapseButton.js'
        },
        plugins: [
            vue()
        ],
    },
    {
        input: 'components/Collapsible.vue',
        output: {
            format: 'esm',
            file: 'regulations/js/Collapsible.js'
        },
        plugins: [
            vue()
        ],
    },
    {
        input: 'components/SupplementaryContent.vue',
        output: {
            format: 'esm',
            file: 'regulations/js/SupplementaryContent.js'
        },
        plugins: [
            vue()
        ],
    },
    {
        input: 'regulations/js/main.js',
        output: {
            file: 'regulations/js/main.build.js',
            format: 'iife',
        },
    },
]

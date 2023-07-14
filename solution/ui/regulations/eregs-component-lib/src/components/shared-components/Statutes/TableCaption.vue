<script setup>
import { computed } from "vue";

import { romanize } from "utilities/utils";

const props = defineProps({
    selectedAct: {
        type: String,
        required: false,
        default: "Social Security Act",
    },
    selectedTitle: {
        type: String,
        required: false,
        default: "19",
    },
});

const romanizedTitle = computed(() =>
    romanize(parseInt(props.selectedTitle, 10))
);
</script>

<template>
    <div class="table__caption">
        In {{ selectedAct }} Title {{ romanizedTitle }}, find equivalent US Code
        citations and read the text in your choice of government website. Learn
        more about these sources:
        <a
            class="external"
            href="https://uscode.house.gov/"
            target="_blank"
            rel="noopener noreferrer"
            >US Code House.gov</a
        >,
        <a
            class="external"
            href="https://www.govinfo.gov/app/collection/comps/"
            target="_blank"
            rel="noopener noreferrer"
            >Statute Compilation</a
        >,
        <a
            class="external"
            href="https://www.govinfo.gov/app/collection/uscode"
            target="_blank"
            rel="noopener noreferrer"
            >US Code Annual</a
        >,
        <a
            class="external"
            href="https://www.ssa.gov/OP_Home/ssact/ssact.htm"
            target="_blank"
            rel="noopener noreferrer"
            >SSA.gov Compilation</a
        >.
    </div>
</template>

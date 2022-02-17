<template>
    <div class="toc-container">
        <template v-for="title in titles">
            <TocTitle :label="title[1].label" :key="title[0]" />
            <template v-for="chapter in Object.entries(title[1].chapters)">
                <h4 :key="chapter[0]">{{ chapter[1].label }}</h4>
                <template
                    v-for="subchapter in Object.entries(chapter[1].subchapters)"
                >
                    <TocSubchapter
                        :label="subchapter[1].label"
                        :parts="subchapter[1].parts"
                        :key="subchapter[0]"
                    />
                </template>
            </template>
        </template>
    </div>
</template>

<script>
import TocTitle from "@/components/homepage/toc/Title.vue";
import TocSubchapter from "@/components/homepage/toc/Subchapter.vue";

export default {
    components: {
        TocSubchapter,
        TocTitle,
    },

    name: "TOC",

    props: {
        structure: {
            type: Object,
            required: true,
        },
    },

    computed: {
        titles() {
            return Object.entries(this.structure);
        },
    },
};
</script>

<style></style>

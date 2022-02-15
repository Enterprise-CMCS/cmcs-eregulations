<template>
    <div class="subchapter">
        <h2>{{ label }}</h2>
        <template v-for="part in partsArr">
            <div class="part-names" :key="part[0]">
                <router-link
                    :to="{
                        name: 'part',
                        params: { title: part[1].title, part: part[1].part },
                    }"
                >
                    <span class="part-number">Part {{ part[0] }} </span>
                    <span>–</span>
                    <span class="part-title"> {{ part[1].description }}</span>
                </router-link>
            </div>
        </template>
    </div>
</template>

<script>
export default {
    name: "TocSubchapter",

    props: {
        label: {
            type: String,
            required: true,
        },
        parts: {
            type: Object,
            required: false,
        },
    },

    computed: {
        partsArr() {
            return Object.entries(this.parts);
        },
    },
};
</script>

<style></style>

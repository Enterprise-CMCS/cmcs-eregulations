<template>
    <div class="sectiondisplay">
    <div>
            <h2 style="display: inline">{{supList.length}} Results</h2>
            <span style="float: right">
                <a>Sort By</a>
            </span></div>
        <SectionCards v-bind:supList="supList" />

    </div>
    
</template>
<script>
import SectionCards from "../PDPart/SectionCards.vue";

export default {
    name: "SectionPane",
    props: ["supList"],
    components: {
        SectionCards,
    },
};
</script>
<style scoped>
.sectiondisplay {
    padding: 30px;
    width:100%;
}
</style>

<template v-slot:extension>
    <div>
        <v-tabs v-model="tab">
            <v-tab v-for="tab in tabs" :key="tab">{{ tab }}</v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
            <v-tab-item v-for="d in data" :key="d"
                ><v-card
                    ><v-card-text>{{ d }}</v-card-text></v-card
                ></v-tab-item
            >
        </v-tabs-items>
    </div>
</template>
<script>
import TabFilters from "./TabFilters.vue";
export default {
    components: {
        TabFilters,
    },
    name: "RightColumn",
    props: {
        title: { type: Number },
        part: { type: Number },
    },
    data() {
        return {
            tab: null,
            tabs: ["Part", "Subpart", "Section"],
            data: ["Part Data", "Subpart Data", "Section Data"],
        };
    },
};
</script>
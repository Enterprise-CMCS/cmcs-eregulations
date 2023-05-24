<template>
    <v-tabs>
        <v-tab>
            Recent Subregulatory Guidance
        </v-tab>
            <v-tab-item>
                <RecentChangesContainer :apiUrl="api_url"></RecentChangesContainer>
            </v-tab-item>

        <v-tab>
            Recent Rules
        </v-tab>
        <v-tab-item>
            <RecentChangesContainer :apiUrl="api_url"></RecentChangesContainer>
            </v-tab-item>
    </v-tabs>
</template>
<script>

import RecentChangesContainer from '../../../eregs-component-lib/src/components/RecentChangesContainer.vue';
export default {
    name: "ResourcesComponent",

    props: {
        api_url: {
            type: String,
            required: true,
        },
    },
    components: {
        RecentChangesContainer,
    },
    data() {
        return {

        };
    },



};
</script>

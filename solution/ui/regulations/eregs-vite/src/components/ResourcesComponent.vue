<template>
    <v-tabs grow>
        <v-tab class="content-tabs">
            Recent Subregulatory Guidance
        </v-tab>
        <v-tab-item grow>
            <RecentChangesContainer :apiUrl="api_url" type="supplemental"></RecentChangesContainer>
        </v-tab-item>

        <v-tab  class="content-tabs">
            Recent Rules
        </v-tab>
        <v-tab-item grow>
            <RecentChangesContainer :apiUrl="api_url" type="rules"></RecentChangesContainer>
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

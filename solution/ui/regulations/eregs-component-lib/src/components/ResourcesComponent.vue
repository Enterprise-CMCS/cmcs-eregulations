<template>
    <v-tabs>
        <v-tab class="content-tabs" grow>
            Recent Subregulatory Guidance
        </v-tab>
        <v-tab-item grow>
            <RecentChangesContainer :apiUrl="api_url" type="supplemental"></RecentChangesContainer>
            <a :href="resource_link" class="action-btn default-btn link-btn">View More Guidance</a>
        </v-tab-item>

        <v-tab class="content-tabs">
            Recent Rules
        </v-tab>
        <v-tab-item grow>
            <RecentChangesContainer :apiUrl="api_url" type="rules"></RecentChangesContainer>
            <a :href="fr_doc_link" class="action-btn default-btn link-btn">View More Changes</a>
        </v-tab-item>
    </v-tabs>
</template>
<script>

import RecentChangesContainer from './RecentChangesContainer.vue';

export default {
    name: "ResourcesComponent",

    props: {
        api_url: {
            type: String,
            required: true,
        },
        resource_link:{
            type: String,
            required: true,
        },
        fr_doc_link: {
            type: String,
            required: true,
        },
    },
    components: {
        RecentChangesContainer,
    }
};
</script>

<template>
    <v-tabs>
        <v-tab id="content-tabs">
            Recent Subregulatory Guidance
        </v-tab>
        <v-tab-item grow>
            <RecentChangesContainer :apiUrl="api_url" type="supplemental" prototype="True"></RecentChangesContainer>
        </v-tab-item>

        <v-tab  id="content-tabs">
            Recent Rules
        </v-tab>
        <v-tab-item grow>
            <RecentChangesContainer :apiUrl="api_url" type="rules" prototype="True"></RecentChangesContainer>
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
<style>
#content-tabs {
    color:#17415f;
    font-family: 'Merriweather';
font-style: normal;
font-weight: 700;
font-size: 24px;
line-height: 36px;
max-width: 800px;
}
</style>

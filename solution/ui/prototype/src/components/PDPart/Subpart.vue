<template>
    <div>
        <h3>Subpart Resources</h3>
        <p>Subpart Description</p>
    
         <ExpansionMenu v-bind:header="'Subparts'" v-bind:subpiece="'Subpart'" v-bind:content="'content'" v-bind="'true'" />

        <br />
        <v-btn color="#046791" class="white--text">View All Resources</v-btn>
    </div>
</template>
<script>

import ExpansionMenu from './ExpansionMenu.vue'

export default({
    name:"SubpartResources",
    components: {
        ExpansionMenu
    },
})
</script>

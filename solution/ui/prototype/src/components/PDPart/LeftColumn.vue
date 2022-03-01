<template>
    <div style="width:100%; margin:20px">
        <div>
            <h2 style="display: inline">
                Title {{ title }} > Part {{ part }}
            </h2>
            <span style="float:right">
                <a>Previous</a>/<a>Next</a>
            </span>
        </div>

        <v-expansion-panels>
            <v-expansion-panel>
                <v-expansion-panel-header>
                    Table of Contents
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    TABLE OF CONTENTS HERE
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>



    </div>
</template>

<script>
export default {
  name: "LeftColumn",
  props:{
    title: {type:Number},
    part: {type: Number},
    
  }
}
</script>

<style scoped>

</style>
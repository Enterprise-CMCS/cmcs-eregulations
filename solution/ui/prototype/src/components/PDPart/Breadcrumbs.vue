<template>
    <span>
        <router-link
            v-if="subPart"
            :to="{
                name: 'PDpart',
                params: { title: this.title, part: this.part },
            }"
        >
            Part {{ this.part }}
        </router-link>
        <span v-else>Part {{ this.part }}</span>
        <template v-if="subPart">
            > 
            <router-link
                v-if="section"
                :to="{
                    name: 'PDpart-subPart',
                    params: { title: this.title, part: this.part, subPart: this.subPart },
                }"
            >
                Subpart {{ this.subPart.split("-")[1] }}</router-link>
            <span v-else>Subpart {{ this.subPart.split("-")[1] }}</span>

            <template v-if="section">
                > <span>§ {{ this.part }}.{{ this.section }}</span>
            </template>
        </template>
    </span>
</template>

<script>
export default {
  name: "Breadcrumbs",
  props: {
      title: {type:String},
      part: {type: String},
      subPart: {type: String},
      section: {type: String},
  },
}
</script>

<style scoped>

</style>
<template>
    <v-card class="flex-row-item">
        <v-card-title>
            <div class="supplemental-content__title">
                {{ formattedDate }}{{ supplementalContent.name ? ` | ${supplementalContent.name}`: "" }}
            </div>
        </v-card-title>
        <v-card-text>
            <div class="supplemental-content__text">
                {{ supplementalContent.description }}
                <a
                    :href="supplementalContent.url"
                    target="_blank"
                ><v-icon>mdi-open-in-new</v-icon></a>
            </div>
        </v-card-text>
    </v-card>
</template>

<script>
export default {
  name: "SupplementalContentCard",
  props: {
      supplementalContent: Object
  },
  computed: {
    formattedDate: function(){
      const date =  new Date(this.supplementalContent.updated_at)
      const options = {year: 'numeric', month: 'long', day: 'numeric' };
      return new Intl.DateTimeFormat('en-US', options).format(date)
    },
  }
}
</script>

<style >
.supplemental-content__title{
  font-size:15px;
  font-weight: bold;
  color: #046791;
}
.supplemental-content__text{
  font-size:15px;
  color: #046791;
  width: 90%
}
</style>
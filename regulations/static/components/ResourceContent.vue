<template>
  <div>
    <div>
      <h2>Filter Resources</h2>
      <label for="part">Part</label>
      <select id="part" v-model="part">
        <option v-for="partOption in partOptions" >{{partOption.part}}</option>

      </select>
      <label for="subPart">SubPart</label>
      <select id="subPart" v-model="subPart">
        <option value="">Select SubPart</option>
        <option value="A">A</option>
        <option value="B">B</option>
        <option value="C">C</option>
      </select>
      <label for="section">Section</label>
      <select id="section" v-model="section">
        <option value="">Select Section</option>
        <option value="A">A</option>
        <option value="B">B</option>
        <option value="C">C</option>
      </select>
      <label for="resourceCategory">Resource Category</label>
      <select id="resourceCategory" v-model="category">
        <option value="">Select Resource Category</option>
        <option value="A">A</option>
        <option value="B">B</option>
        <option value="C">C</option>
      </select>
    </div>

    <div>
      <ul>
        <li>Selected Part: {{ part }}</li>
        <li>Selected SubPart: {{ subPart }}</li>
        <li>Selected Section?: {{ section }}</li>
        <li>Selected Category?: {{ category }}</li>
      </ul>
    </div>

  </div>
</template>

<script>
const fecthedData = [{"title":42,"part":44},{"title":42,"part":400},{"title":42,"part":430},{"title":42,"part":431},{"title":42,"part":432},{"title":42,"part":433},{"title":42,"part":434},{"title":42,"part":435},{"title":42,"part":436},{"title":42,"part":438},{"title":42,"part":440},{"title":42,"part":441},{"title":42,"part":442},{"title":42,"part":445},{"title":42,"part":447},{"title":42,"part":455},{"title":42,"part":456},{"title":42,"part":457},{"title":42,"part":460},{"title":42,"part":4545}]
export default {
  props: {
    api_url: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
  },
  data: function(){
    return {
      part: '',
      partOptions: [{part:"Loading"}],
      subPart: '',
      section:'',
      category:'',
    }
  },
  created: function(){
    this.getParts(this.title)
  },
  methods:{
    async getParts(title){
      console.log(title)
      try {
        const response = await fetch(
            `${this.api_url}title/${title}/parts`
        );
        const content = await response.json();
        console.log(content)
        this.partOptions = content;
      } catch (error) {
          console.error(error);
      }
    },

  }
}
</script>

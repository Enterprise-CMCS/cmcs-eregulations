<template>
    <div>
        <div>
            <h2 style="display: inline">
                Part {{ part }} resources
            </h2>
            <span style="float:right">
                <a>Filter and sort resources</a>
            </span>
        </div>
        Right Side
    </div>
</template>

<script>
export default {
  name: "RightColumn",
  props:{
    title: {type:Number},
    part: {type: Number}
  }
}
</script>

<style scoped>

</style>
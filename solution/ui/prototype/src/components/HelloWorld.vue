<template>
    <v-container>
        <p>{{ msg }}</p>
    </v-container>
</template>

<script>
export default {
    name: "HelloWorld",

    props: {
        msg: String,
        default: "Hello World!",
    },
};
</script>

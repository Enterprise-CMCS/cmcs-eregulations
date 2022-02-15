<template>
    <div class="dot-loader">
        <div class="dot-flashing"></div>
    </div>
</template>

<script>
export default {
    name: 'InlineLoader'
};
</script>

<style lang="scss">
/**
 * ==============================================
 * Dot Flashing
 * https://codepen.io/nzbin/pen/GGrXbp
 * ==============================================
 */
$light-color: #a3e8ff;
$dark-color: #17515f;

.dot-loader {
    display: inline-block;
    width: 40px;
    margin: 0 5px;
}

.dot-flashing {
    position: relative;
    margin: auto;
    width: 10px;
    height: 10px;
    border-radius: 5px;
    background-color: $dark-color;
    color: $dark-color;
    animation: dotFlashing 1s infinite linear alternate;
    animation-delay: 0.5s;
}

.dot-flashing::before,
.dot-flashing::after {
    content: "";
    display: inline-block;
    position: absolute;
    top: 0;
}

.dot-flashing::before {
    left: -15px;
    width: 10px;
    height: 10px;
    border-radius: 5px;
    background-color: $dark-color;
    color: $dark-color;
    animation: dotFlashing 1s infinite alternate;
    animation-delay: 0s;
}

.dot-flashing::after {
    left: 15px;
    width: 10px;
    height: 10px;
    border-radius: 5px;
    background-color: $dark-color;
    color: $dark-color;
    animation: dotFlashing 1s infinite alternate;
    animation-delay: 1s;
}

@keyframes dotFlashing {
    0% {
        background-color: $dark-color;
    }
    50%,
    100% {
        background-color: $light-color;
    }
}
</style>

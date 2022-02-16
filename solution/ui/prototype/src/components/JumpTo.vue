<template>
    <div class="jump-to">
        <div v-if="header !== ''" class="jump-to-label">
            {{ header }}
        </div>

        <form method="GET" action="">
            <input name="-version" type="hidden" required value="" />
            <div class="jump-to-input">
                <select v-if="defaultTitle !== ''" name="title" class="ds-c-field" required>
                    <option value="" disabled selected>Title</option>
                </select>
                §
                <select
                    name="part"
                    class="ds-c-field"
                    aria-label="Regulation part number"
                    required
                >
                    <option value="" disabled selected>Part</option>
                </select>
                <span class="dot">.</span>
                <input
                    class="number-box ds-c-field"
                    name="section"
                    placeholder=""
                    type="text"
                    pattern="\d+"
                    title="Regulation section number, i.e. 111"
                    aria-label="Regulation section number, i.e. 111"
                />
            </div>

            <input class="submit" type="submit" value="Go" />
        </form>
    </div>
</template>

<script>
export default {
    props: ["header", "defaultTitle"],
};
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.jump-to .dot {
    margin: 0 5px;
}
.jump-to select{
     border: 1px solid #D6D7D9;
}
.jump-to input.submit {
    border: solid 1px #D6D7D9;
    color: #A3A3A3;
    background-color: white;
}
.jump-to .number-box{
    border: #D6D7D9 1px solid
}
</style>

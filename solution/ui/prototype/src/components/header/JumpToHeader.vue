<template>
    <div class="jump-to">
        <form method="GET" action="">
            <input name="-version" type="hidden" required value="" />

            <div class="jump-to-input">
                <select name="title" class="ds-c-field" required>
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
export default {};
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.jump-to .dot {
    margin: 0 5px;
}

input.submit {
    color: black;
}
</style>

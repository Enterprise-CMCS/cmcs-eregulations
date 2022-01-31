<template>
    <div class="jump-to">
        <div class="jump-to-label">
            Jump to Regulation Section
        </div>

        <form
            method="GET"
            action=""
        >
            <input
                name="-version"
                type="hidden"
                required
                value=""
            />
            <input
                name="title"
                type="hidden"
                required
                value="42"
            />

            <div class="jump-to-input">
                §
                <select
                    name="part"
                    class="ds-c-field"
                    aria-label="Regulation part number"
                ></select>
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

            <input
                class="submit"
                type="submit"
                value="Go"
            />
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

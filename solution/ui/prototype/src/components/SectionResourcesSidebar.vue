<template>
    <div class="sidebar-container">
        <h3>Resources</h3>
        <p class="empty-state-text">
            Resource links are curated and updated by a Medicaid subject matter
            expert on our team. Select a subpart or section on the left to view
            associated resources.
        </p>
    </div>
</template>

<script>
export default {
    name: "SectionResourcesSidebar",

    props: {
        title: String,
        part: String,
        selectedIdentifier: String,
        selectedScope: String,
    },
};
</script>

<style>
.sidebar-container h3 {
    margin-top: 0px;
    font-size: 24px;
}

.empty-state-text {
    margin-top: 20px;
    font-size: 14px;
    color: #8C8C8C;
}
</style>

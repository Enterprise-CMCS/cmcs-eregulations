<script setup>
import { computed, ref } from "vue";

defineProps({
    searchUrl: {
        type: String,
        required: true,
    },
});

const mobileSearchExpanded = ref(false);

const expandSearchClick = () => {
    mobileSearchExpanded.value = !mobileSearchExpanded.value;
};

const expandStateClasses = computed(() => ({
    hidden: !mobileSearchExpanded.value,
    visible: mobileSearchExpanded.value,
}));
</script>

<template>
    <form class="search__form" :action="searchUrl">
        <button
            type="button"
            class="form__button--close-mobile-search"
            aria-label="Close Search Bar"
            @click="expandSearchClick"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="10"
                height="22"
                viewBox="0 -2 10 18"
                fill="none"
            >
                <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M8.96941 17.5165C8.85444 17.6351 8.72305 17.6923 8.57524 17.6923C8.42332 17.6923 8.29398 17.6351 8.17902 17.5165L0.170395 9.25489C0.0554291 9.1363 -3.93436e-07 9.00075 -3.86678e-07 8.84615C-3.80012e-07 8.69367 0.0554291 8.55813 0.170395 8.43953L8.17902 0.177897C8.29398 0.0614168 8.42332 -6.89188e-08 8.57524 -6.22782e-08C8.72305 -5.5817e-08 8.85444 0.0614169 8.96941 0.177897L9.82755 1.06315C9.94252 1.18175 10 1.3194 10 1.47189C10 1.62649 9.94252 1.76203 9.82755 1.88063L3.07534 8.84615L9.82755 15.8138C9.94252 15.9324 10 16.0679 10 16.2225C10 16.375 9.94252 16.5106 9.82755 16.6292L8.96941 17.5165Z"
                    fill="#046791"
                />
            </svg>
        </button>
        <input
            :class="expandStateClasses"
            type="search"
            name="q"
            placeholder="Search"
        />
        <button
            type="submit"
            class="search__button--submit"
            :class="expandStateClasses"
            aria-label="Search"
        >
            <i class="fa fa-search"></i>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="22"
                height="24"
                viewBox="0 -2 22 20"
                fill="none"
            >
                <path
                    d="M14.9012 8.09846C14.9012 4.59913 11.9002 1.79966 8.3819 1.79966C4.76009 1.79966 1.86265 4.59913 1.86265 8.09846C1.86265 11.4978 4.76009 14.3973 8.3819 14.3973C11.9002 14.3973 14.9012 11.4978 14.9012 8.09846ZM15.2116 12.6976L21.2135 18.3965C22.0413 19.2963 20.7995 20.5961 19.8682 19.6963L13.9698 13.9973C12.5211 15.3971 10.555 16.1969 8.3819 16.1969C3.72529 16.1969 0 12.4976 0 8.09846C0 3.59932 3.72529 0 8.3819 0C12.935 0 16.7638 3.59932 16.7638 8.09846C16.7638 9.79814 16.1429 11.3978 15.2116 12.6976Z"
                    fill="#046791"
                />
            </svg>
        </button>
    </form>
</template>

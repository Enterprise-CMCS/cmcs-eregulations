<script setup>
import { titleSelectorList } from "./schemas/listSchemas";
</script>

<template>
    <ul class="acts__list">
        <li
            v-for="(value, key, i) in titleSelectorList"
            :key="`${key}-${i}`"
            class="acts-list__item"
        >
            <h4>{{ value.name }}</h4>
            <ul class="titles__list">
                <li
                    v-for="(title, j) in value.titles"
                    :key="`${title.title}-${j}`"
                    class="titles-list__item"
                >
                    <h4>
                        <router-link
                            :to="{
                                name: 'statutes',
                                query: {
                                    act: key,
                                    title: title.title,
                                },
                            }"
                        >
                            Title {{ title.titleRoman }} / {{ title.title }}
                        </router-link>
                    </h4>
                </li>
            </ul>
        </li>
</template>

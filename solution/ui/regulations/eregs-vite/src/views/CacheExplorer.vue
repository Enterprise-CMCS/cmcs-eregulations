<template>
    <div id="app" class="cache-explorer">
        CACHE EXPLORER
        <ul>
            <li v-for="key in cacheKeys" :key="key">
                {{ key }}
                <v-btn
                    class="button"
                    @click="deleteCacheItem(key)"
                >
                    Delete
                </v-btn>
                <v-btn class="button" @click="editData(key)">
                    Edit
                </v-btn>
            </li>
            <li>
                <v-btn
                    class="button"
                    @click="deleteAllCacheItems()"
                >
                    Delete All Cache Items
                </v-btn>
            </li>
        </ul>
        <v-divider />
        <v-container fluid>
            <v-row>
                <v-label cols="2" for="path">
                    Path:
                </v-label>
                <v-text-field
                    id="path"
                    v-model="path"
                    outlined
                    cols="8"
                    name="path"
                />
            </v-row>
            <v-row>
                <v-label cols="2">
                    Data:
                </v-label>
                <v-textarea
                    v-model="apiData"
                    outlined
                    cols="8"
                />
            </v-row>
            <v-row>
                <v-btn @click="addToCache">
                    Add to Cache
                </v-btn>
            </v-row>
        </v-container>
        <div v-if="JSONError">
            INVALID JSON
        </div>
    </div>
</template>

<script>
import {
    getCacheKeys,
    removeCacheItem,
    getCacheItem,
    setCacheItem,
} from "utilities/api.js";

const formatKey = (key) => key.replace("GET", "");

export default {
    name: "CacheExplorer",

    components: {},

    data() {
        return {
            cacheKeys: "",
            path: "",
            apiData: "",
            JSONError: false,
        };
    },
    methods: {
        deleteCacheItem: async function (key) {
            console.info("Clearing Key: ", key);
            await removeCacheItem(key);
            this.cacheKeys = await getCacheKeys();
        },
        deleteAllCacheItems: async function () {
            this.cacheKeys.forEach(async (key) => {
                await removeCacheItem(key);
            });
            this.cacheKeys = await getCacheKeys();
        },
        editData: async function (key) {
            this.path = formatKey(key);
            this.apiData = JSON.stringify(await getCacheItem(key));
        },
        addToCache: async function () {
            try {
                await setCacheItem(
                    `GET${this.path}`,
                    JSON.parse(this.apiData)
                );
                this.path = "";
                this.apiData = "";
            } catch {
                this.JSONError = true;
            }

            this.cacheKeys = await getCacheKeys();
        },
    },

    async created() {
        try {
            this.cacheKeys = await getCacheKeys();
        } catch (error) {
            console.error(error);
        }
    },
};
</script>

<style lang="scss">
.cache-explorer {
    .button {
        margin: 7px;
    }
    .v-divider {
        margin: 10px;
    }
     .v-input__slot {
        max-width: 90%;
     }
}
</style>

import _filter from "lodash/filter";
import _get from "lodash/get";
import _isArray from "lodash/isArray";
import _isBoolean from "lodash/isBoolean";
import _isFunction from "lodash/isFunction";
import _isNil from "lodash/isNil";
import _isObject from "lodash/isObject";
import _isUndefined from "lodash/isUndefined";
import _keys from "lodash/keys";
import _map from "lodash/map";
import _set from "lodash/set";
import _setWith from "lodash/setWith";
import _sortedUniq from "lodash/sortedUniq";
import localforage from "localforage";

import { delay, getKebabDate, niceDate, parseError } from "./utils";

const apiPath = `${process.env.VUE_APP_API_URL}/v2`;

let config = {
    apiPath,
    fetchMode: "cors",
    maxRetryCount: 2,
};

localforage.config({
    name: "eregs",
    version: 1.0,
    storeName: "eregs_django", // Should be alphanumeric, with underscores.
});

let token;
let decodedIdToken;
const authHeader = (tok) => ({
    Authorization: `Bearer ${tok}`,
    "Content-Type": "application/json",
});

function setIdToken(encId) {
    token = encId;
    console.log("token is: ", token);
}

function getDecodedIdToken() {
    return decodedIdToken;
}

function forgetIdToken() {
    token = undefined;
    decodedIdToken = undefined;
}

function configure(obj) {
    config = { ...config, ...obj };
}

function fetchJson(url, options = {}, retryCount = 0) {
    // see https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
    let isOk = false;
    let httpStatus;

    const headers = {
        Accept: "application/json",
        "Content-Type": "application/json",
    };
    const body = {};
    const merged = {
        method: "GET",
        cache: "no-cache",
        mode: config.fetchMode,
        redirect: "follow",
        body,
        ...options,
        headers: { ...headers, ...options.headers },
    };

    if (merged.method === "GET") delete merged.body; // otherwise fetch will throw an error
    if (merged.params) {
        // if query string parameters are specified then add them to the URL
        // The merged.params here is just a plain JavaScript object with key and value
        // For example {key1: value1, key2: value2}

        // Get keys from the params object such as [key1, key2] etc
        const paramKeys = _keys(merged.params);

        // Filter out params with undefined or null values
        const paramKeysToPass = _filter(
            paramKeys,
            (key) => !_isNil(_get(merged.params, key))
        );
        const query = _map(
            paramKeysToPass,
            (key) =>
                `${encodeURIComponent(key)}=${encodeURIComponent(
                    _get(merged.params, key)
                )}`
        ).join("&");
        url = query ? `${url}?${query}` : url;
    }

    return (
        Promise.resolve()
            .then(() => localforage.getItem(url.replace(apiPath, merged.method)))
            .then((value) => {
                if (value && Date.now() < value.expiration_date) {
                    console.log("CACHE HIT");
                    return value;
                } else {
                    console.log("CACHE MISS");
                    return fetch(url, merged);
                }
            })
            .catch((err) => {
                // this will capture network/timeout errors, because fetch does not consider http Status 5xx or 4xx as errors
                if (retryCount < config.maxRetryCount) {
                    let backoff = retryCount * retryCount;
                    if (backoff < 1) backoff = 1;

                    return Promise.resolve()
                        .then(() =>
                            console.log(
                                `Retrying count = ${retryCount}, Backoff = ${backoff}`
                            )
                        )
                        .then(() => delay(backoff))
                        .then(() => fetchJson(url, options, retryCount + 1));
                }
                throw parseError(err);
            })
            .then((response) => {
                isOk = response.ok;
                httpStatus = response.status;
                return response;
            })
            .then((response) => {
                if (_isFunction(response.text)) return response.text();
                return response;
            })
            .then((text) => {
                let json;
                try {
                    if (_isObject(text)) {
                        json = text;
                    } else {
                        json = JSON.parse(text);
                    }
                } catch (err) {
                    if (httpStatus >= 400) {
                        if (
                            httpStatus >= 501 &&
                            retryCount < config.maxRetryCount
                        ) {
                            let backoff = retryCount * retryCount;
                            if (backoff < 1) backoff = 1;

                            return Promise.resolve()
                                .then(() =>
                                    console.log(
                                        `Retrying count = ${retryCount}, Backoff = ${backoff}`
                                    )
                                )
                                .then(() => delay(backoff))
                                .then(() =>
                                    fetchJson(url, options, retryCount + 1)
                                );
                        }
                        throw parseError({
                            message: text,
                            status: httpStatus,
                        });
                    } else {
                        throw parseError(
                            new Error(
                                "The server did not return a json response."
                            )
                        );
                    }
                }

                return json;
            })
            .then((json) => {
                if (_isBoolean(isOk) && !isOk) {
                    throw parseError({ ...json, status: httpStatus });
                } else {
                    json.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
                    localforage.setItem(
                        url.replace(apiPath, merged.method),
                        json
                    );
                    return json;
                }
            })
    );
}

// ---------- helper functions ---------------

function httpApiMock(verb, urlPath, { data, params, response } = {}) {
    console.log(`Performing an HTTP ${verb} to ${config.apiPath}/${urlPath}`);
    data && console.log("DATA: ", data);
    params && console.log("PARAMS: ", params);
    response && console.log("RESPONSE: ", response);
    return response;
}

function httpApiGet(urlPath, { params } = {}) {
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "GET",
        headers: authHeader(token),
        params,
    });
}

function httpApiPost(urlPath, { data = {}, params } = {}) {
    console.log(data);
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "POST",
        headers: authHeader(token),
        params,
        body: JSON.stringify(data),
    });
}

// eslint-disable-next-line no-unused-vars
function httpApiPut(urlPath, { data, params } = {}) {
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "PUT",
        headers: authHeader(token),
        params,
        body: JSON.stringify(data),
    });
}

// eslint-disable-next-line no-unused-vars
function httpApiDelete(urlPath, { data, params } = {}) {
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "DELETE",
        headers: authHeader(token),
        params,
        body: JSON.stringify(data),
    });
}
// ---------- cache helpers -----------

const getCacheKeys = async () => {
    return localforage.keys();
};

const removeCacheItem = async (key) => {
    return localforage.removeItem(key);
};

const getCacheItem = async (key) => {
    return localforage.getItem(key);
};

const setCacheItem = async (key, data) => {
    data.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
    return localforage.setItem(key, data);
};

// ---------- api calls ---------------
const getLastUpdatedDate = async (title = "42") => {
    const reducer = (accumulator, currentValue) => {
        return currentValue.date > accumulator.date
            ? currentValue
            : accumulator;
    };

    const result = await httpApiGet(`title/${title}/existing`);

    return niceDate(_get(result.reduce(reducer), "date"));
};

const getPartNames = async (title = "42") => {
    const result = await httpApiGet(`title/${title}/existing`);

    return _sortedUniq(result.flatMap((part) => part.partName).sort());
};

const getHomepageStructure = async () => {
    const reducer = (accumulator, currentValue) => {
        const title = currentValue.title;
        const chapter = _get(
            currentValue,
            "structure.children[0].identifier[0]"
        );
        const subchapter = _get(
            currentValue,
            "structure.children[0].children[0].identifier[0]"
        );
        const part = _get(
            currentValue,
            "structure.children[0].children[0].children[0].identifier[0]"
        );
        const partLabel = _get(
            currentValue,
            "structure.children[0].children[0].children[0].label"
        );
        const partDescription = _get(
            currentValue,
            "structure.children[0].children[0].children[0].label_description"
        );

        if (
            _isUndefined(title) ||
            _isUndefined(chapter) ||
            _isUndefined(subchapter) ||
            _isUndefined(part)
        ) {
            return accumulator;
        }

        const contentToSet = {
            title,
            chapter,
            subchapter,
            part,
            label: partLabel,
            description: partDescription,
            type: "part",
        };

        _setWith(
            accumulator,
            `${title}.chapters.${chapter}.subchapters.${subchapter}.parts.${part}`,
            contentToSet,
            Object
        );

        // if no title label, set it
        if (_isUndefined(accumulator[title].label)) {
            _set(
                accumulator,
                `${title}.label`,
                _get(currentValue, "structure.label")
            );
            _set(
                accumulator,
                `${title}.type`,
                _get(currentValue, "structure.type")
            );
        }

        // if no chapter label, set it
        if (_isUndefined(accumulator[title].chapters[chapter].label)) {
            _set(
                accumulator,
                `${title}.chapters.${chapter}.label`,
                _get(currentValue, "structure.children[0].label")
            );
            _set(
                accumulator,
                `${title}.chapters.${chapter}.type`,
                _get(currentValue, "structure.children[0].type")
            );
        }

        // if no subchapter label, set it
        if (
            _isUndefined(
                accumulator[title].chapters[chapter].subchapters[subchapter]
                    .label
            )
        ) {
            _set(
                accumulator,
                `${title}.chapters.${chapter}.subchapters.${subchapter}.label`,
                _get(currentValue, "structure.children[0].children[0].label")
            );
            _set(
                accumulator,
                `${title}.chapters.${chapter}.subchapters.${subchapter}.type`,
                _get(currentValue, "structure.children[0].children[0].type")
            );
        }

        return accumulator;
    };

    const result = await getAllParts()

    const transformedResult = result.reduce(reducer, {});

    return transformedResult;
};

const getAllParts = async () =>{
    return  await httpApiGet("all_parts");
}
const getCategories = async () => {
    return  await httpApiGet("categories");
}

const getPartsList = async () =>{
    const all_parts = await getAllParts()
    return all_parts.map(d => d.name)


}
const getSubPartsForPart = async (part) =>{
    const all_parts = await getAllParts()
    const parts = all_parts.map(d => d.name)
    const potentialSubParts = all_parts[parts.indexOf(part)].structure.children[0].children[0].children[0].children
    const subParts = potentialSubParts.filter(p=>p.type==="subpart")
    return subParts.map(s => s.identifier[0])

}

const getSectionsForSubPart = async (part, subPart) =>{
    const all_parts = await getAllParts()
    const parts = all_parts.map(d => d.name)
    const potentialSubParts = all_parts[parts.indexOf(part)].structure.children[0].children[0].children[0].children
    const parent = potentialSubParts.find(p=>p.type==="subpart" && p.identifier[0] === subPart )
    return parent.children.map(c => c.identifier[1])

}


const getPart = async (title, part) => {
    const result = await httpApiGet(
        `${getKebabDate()}/title/${title}/part/${part}`
    );

    // mixing lodash get and optional chaining.  Both provide safeguards and do the same this
    const toc = result?.toc;

    const orphansAndSubparts = _get(result, "document.children");

    return [toc, orphansAndSubparts];
};

const getSupplementalContent = async (
    title = "42",
    part,
    scope,
    identifier
) => {
    const result = await httpApiGet(
        `title/${title}/part/${part}/supplemental_content?&${scope}s=${identifier}`
    );
    return result;
};

const getSupplementalContentNew = async (
    title,
    part,
    sections =[],
    subparts= []
) => {
    let sString = '';
    for (let s in sections) {
        sString = sString + "&sections=" + sections[s]
    }
    for(let sp in subparts){
        sString = sString + "&subparts=" + subparts[sp]
    }
    const result = await httpApiGet(
        `title/${title}/part/${part}/supplemental_content?${sString}`
    );
    
    return result;
};
const getSupplementalContentCountForPart = async (part) =>{
        const result = await httpApiGet(
        `supplemental_content_count_by_part?part=${part}`
    );
    return result;
}

// API Functions Insertion Point (do not change this text, it is being used by hygen cli)

export {
    configure,
    setIdToken,
    getDecodedIdToken,
    forgetIdToken,
    config,
    getLastUpdatedDate,
    getHomepageStructure,
    getPartNames,
    getAllParts,
    getSubPartsForPart,
    getPart,
    getCacheKeys,
    removeCacheItem,
    getCacheItem,
    setCacheItem,
    getSupplementalContent,
    getSupplementalContentNew,
    getPartsList,
    getSectionsForSubPart,
    getSupplementalContentCountForPart,
    getCategories
    // API Export Insertion Point (do not change this text, it is being used by hygen cli)
};

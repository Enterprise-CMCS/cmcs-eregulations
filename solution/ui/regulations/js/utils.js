/* eslint-disable */
import _delay from "lodash/delay";
import _get from "lodash/get";

// a promise friendly delay function
function delay(seconds) {
    return new Promise((resolve) => {
        _delay(resolve, seconds * 1000);
    });
}

function parseError(err) {
    console.log(err);
    const errMessage = err.errors
        ? err.errors[Object.keys(err.errors)[0]][0]
        : err.message;
    errMessage && alert(errMessage);

    const message = errMessage;
    try {
        const code = Object.keys(err.errors)[0];
        const status = _get(err, "status");
        const requestId = _get(err, "requestId");
        const error = new Error(message);
        error.code = code;
        error.requestId = requestId;
        error.root = err;
        error.status = status;

        return error;
    } catch {
        return new Error(message);
    }
}

const EventCodes = {
    SetSection: 'SetSection'
}

const formatResourceCategories = (resources) => {
    const rawCategories = JSON.parse(
        document.getElementById("categories").textContent
    );

    resources.filter((resource)=> resource.category.type ==="category").forEach(resource => {
        const existingCategory = rawCategories.find(category => category.name === resource.category.name)

        if (existingCategory){
            if (!existingCategory.supplemental_content){
                existingCategory.supplemental_content = []
            }
            existingCategory.supplemental_content.push(resource)
            console.log(existingCategory)

        } else{
          const newCategory = JSON.parse(JSON.stringify(resource.category))
          newCategory.supplemental_content = [resource]
          newCategory.sub_categories = []
          rawCategories.push(newCategory)
        }
    })

    const rawSubCategories = JSON.parse(
        document.getElementById("sub_categories").textContent
    );

    resources.filter((resource)=> resource.category.type ==="subcategory").forEach(resource => {
        const existingSubCategory = rawSubCategories.find(category => category.name === resource.category.name)

        if (existingSubCategory){
            if (!existingSubCategory.supplemental_content){
                existingSubCategory.supplemental_content = []
            }
            existingSubCategory.supplemental_content.push(resource)

        } else{
          const newSubCategory = JSON.parse(JSON.stringify(resource.category))
          newSubCategory.supplemental_content = [resource]
          rawSubCategories.push(newSubCategory)
        }
    })
    const categories = rawCategories.map((c) => {
        const category = JSON.parse(JSON.stringify(c));
        category.sub_categories = rawSubCategories.filter(
            (subcategory) => subcategory.parent.id === category.id
        );
        return category;
    });
    categories.sort((a, b) =>
        a.order - b.order
    );
    categories.forEach((category) => {
        category.sub_categories.sort((a, b) =>
            a.order - b.order
        );
    });
    return categories
}

function flattenSubpart(subpart){
    const result = JSON.parse(JSON.stringify(subpart))
    const subjectGroupSections = subpart.children
        .filter(child => child.type=== 'subject_group')
        .flatMap(subjgrp => subjgrp.children)
        .filter(child => child.type ==="section")


    result.children = result.children
        .concat(subjectGroupSections)
        .filter(child => child.type ==="section")

    return result
}

export {
    delay,
    parseError,
    formatResourceCategories,
    EventCodes,
    flattenSubpart
};

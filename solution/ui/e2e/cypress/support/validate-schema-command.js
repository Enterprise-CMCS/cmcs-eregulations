import Ajv from "ajv";

const getSchemaError = (getAjvError) => {
    return cy.wrap(
        `Field: ${getAjvError[0]["instancePath"]} is invalid. Cause: ${getAjvError[0]["message"]}`
    );
};

export const validateSchema = (schema, response) => {
    const ajv = new Ajv();
    const validate = ajv.compile(schema);
    const valid = validate(response);

    if (!valid) {
        getSchemaError(validate.errors).then((schemaError) => {
            throw new Error(schemaError);
        });
    } else {
        cy.log("Schema validated!");
    }
};

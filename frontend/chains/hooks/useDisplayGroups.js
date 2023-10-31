import React from "react";

/**
 * Converts a JSONSchema into a sub-schemas for each field_group. The sub-schemas
 * are used to render collapsible sections in the JSONSchemaForm. Since each is
 * a sub-schema, they can be rendered with a JSONSchemaForm.
 *
 *  - groups secrets by secret_key
 *  - groups fields by field_group
 *  - secret_keys are added to field_groups based on their keys.
 *  - fields not assigned to a field_group are added to the default group
 */
export const useDisplayGroups = (schema) => {
  return React.useMemo(() => {
    // build secret_groups
    // HAX: disabled until secrets backend is ready.
    const secret_groups = {};
    if (false) {
      for (const key of Object.keys(schema.properties)) {
        const property = schema.properties[key];
        if (property.input_type === "secret") {
          const secret_key = property.secret_key || key;
          if (!secret_groups[secret_key]) {
            secret_groups[secret_key] = [];
            secret_groups[secret_key] = {
              type: "secret",
              input_type: "secret_select",
              properties: [],
            };
          }
          secret_groups[secret_key].properties.push(key);
        }
      }
    }

    // build sub-schemas for each field_group.
    const field_groups = {};
    const seen = new Set();
    if (schema.display_groups) {
      for (const group of schema.display_groups) {
        const key = group.key;

        // init field group if needed
        if (!field_groups[key]) {
          field_groups[key] = {
            order: group.fields,
            required: schema.required,
            properties: {},
          };
        }

        for (const field_name of group.fields) {
          if (secret_groups[field_name]) {
            // secrets are added to field_group as a group.
            field_groups[key].properties[field_name] =
              secret_groups[field_name];
          } else {
            // regular properties are added individually
            const property = schema.properties[field_name];
            if (!property) {
              console.warn("property not found: ", field_name);
              continue;
            }
            field_groups[key].properties[field_name] = property;
          }
          seen.add(field_name);
        }
      }
    }

    // add any properties and secrets that were not in the field_groups to the default group.
    const defaultGroup = { order: [], properties: {} };
    for (const key of Object.keys(schema.properties)) {
      const property = schema.properties[key];

      // HAX: disabling secret groups until secrets backend is ready.
      if (false && property.input_type === "secret" && !seen.has(key)) {
        const secret_key = property.secret_key || key;
        if (!seen.has(secret_key)) {
          defaultGroup.properties[secret_key] = secret_groups[secret_key];
          defaultGroup.order.push(secret_key);
        }
      } else if (!seen.has(key)) {
        defaultGroup.properties[key] = property;
        defaultGroup.order.push(key);
      }
    }

    if (defaultGroup.properties) {
      defaultGroup.order.sort();
      field_groups.default = defaultGroup;
    }

    return field_groups;
  }, [schema]);
};

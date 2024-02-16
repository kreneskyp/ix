import React from "react";
import { AsyncSelect } from "chakra-react-select";
import { useChakraStyles } from "components/select/useChakraStyles";
import { useSelectStyles } from "components/select/useSelectStyles";

/**
 * An extension of chakra-react-select that encapsulates the logic for loading
 * options and values from the API.
 *
 * @param {function} onChange - callback for when the value changes, will receive
 *  the value as a parameter
 * @param {string} value - the current value (id) of the object
 * @param {function} getOptions - a function that returns options for a search arg
 * @param {function} getDefaultOptions - a function that returns default options to display
 * before the user has entered a search term.
 * @param {function} getDetail - a function that returns the detail for a given value
 * when rendering the component for the first time. This is necessary because the
 * component is async and the value may not be available yet.
 */
export const AsyncAPIObjectSelect = ({
  onChange,
  value,
  getOptions,
  getDefaultOptions,
  getDetail,
  ...props
}) => {
  const [selected, setSelected] = React.useState(null);
  const chakraStyles = useChakraStyles();

  // load value on initial render
  React.useEffect(() => {
    const callback = async () => {
      const selectedValue = await getDetail(value);
      setSelected(selectedValue);
    };
    callback();
  }, [onChange, value]);

  const promiseOptions = (inputValue) =>
    new Promise((resolve) => {
      setTimeout(() => {
        getOptions(inputValue)
          .then((options) => {
            resolve(options);
          })
          .catch((error) => {
            resolve([]);
          });
      }, 500);
    });

  const handleChange = (newValue) => {
    setSelected(newValue);
    onChange(newValue.value);
  };

  return (
    <AsyncSelect
      onChange={handleChange}
      loadOptions={promiseOptions}
      value={selected}
      defaultOptions={true}
      cacheOptions
      styles={useSelectStyles()}
      menuPortalTarget={document.body}
      chakraStyles={chakraStyles}
      {...props}
    />
  );
};

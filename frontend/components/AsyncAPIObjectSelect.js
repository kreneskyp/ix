import React from "react";
import { AsyncSelect } from "chakra-react-select";
import { useEditorColorMode } from "chains/editor/useColorMode";

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
  const [options, setOptions] = React.useState([]);
  const { input: styles } = useEditorColorMode();

  // load value on initial render
  React.useEffect(() => {
    const callback = async () => {
      if (selected === null && value) {
        setSelected(getDetail(value));
      }
    };
    callback();
  }, [value]);

  // load defaults on initial render
  React.useEffect(() => {
    setOptions(getDefaultOptions());
  }, []);

  const chakraStyles = {
    control: (base) => ({ ...base, ...styles }),
    dropdownIndicator: (base) => ({ ...base, ...styles }),
  };

  const promiseOptions = (inputValue) =>
    new Promise((resolve) => {
      setTimeout(() => {
        getOptions(inputValue)
          .then((options) => {
            setOptions(options);
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
      defaultOptions={options}
      cacheOptions
      styles={{
        menuPortal: (base) => ({ ...base, zIndex: 99999 }),
      }}
      menuPortalTarget={document.body}
      chakraStyles={chakraStyles}
    />
  );
};

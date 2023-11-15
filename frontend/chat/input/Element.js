import React from "react";

export const Element = ({ highlights, ...props }) => {
  const { attributes, children, element } = props;
  const highlight_elements = highlights.reduce((map, highlight) => {
    map[highlight.type] = highlight.element;
    return map;
  }, {});

  if (highlight_elements[element.type]) {
    const HighlightElement = highlight_elements[element.type];
    return <HighlightElement {...props} />;
  }
  return <p {...attributes}>{children}</p>;
};

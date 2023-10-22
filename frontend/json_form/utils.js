export const getLabel = (name) => name || labelify(name || "");

export const labelify = (key) => {
  return key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

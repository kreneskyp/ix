import { useEffect, useState } from "react";
import { v4 as uuid4 } from "uuid";

/**
 * Hook for handling the state of an object editor view.
 * state for handling whether how to load the data (new vs existing)
 * and when to reset the editor when opened. The cached state does not
 * reset when the url changes as protection against reloading when
 * creating new chains. This state tracks when to reset the cache.
 *
 * @param id - object id, or undefined/null if new
 * @param load - function to load the object when needed
 */
export const useObjectEditorView = (id, load) => {
  const [idRef, setIdRef] = useState(null);
  const [isNew, setIsNew] = useState(null);
  const [wasCreated, setWasCreated] = useState(null);
  useEffect(() => {
    const firstRender = isNew === null;
    if (firstRender) {
      // first render caches whether this started as a new chain
      setIsNew(id === undefined);
    } else {
      // switch from existing to new
      if (id === undefined && !isNew) {
        setIsNew(true);
        setWasCreated(false);
      }
      // a new chain was created
      if (id !== undefined && isNew) {
        setWasCreated(true);
      }
      // switch from created to new
      if (id === undefined && wasCreated) {
        setIsNew(true);
        setWasCreated(false);
        setIdRef(uuid4());
      }
    }
  }, [id]);

  useEffect(() => {
    // load chain if id is provided on view load
    // otherwise state will be handled internally by the editor
    if (isNew === false) {
      load();
      setIdRef(id);
    } else {
      // create a uuid here to force a new editor. This helps detect
      // creating a new object after a new object was just created.
      setIdRef(uuid4());
    }
  }, [isNew]);

  return {
    isNew,
    idRef,
    wasCreated,
  };
};

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
  const [urlChanged, setUrlChanged] = useState(false);
  const [prevId, setPrevId] = useState(null);

  useEffect(() => {
    const firstRender = isNew === null;
    if (firstRender) {
      setIsNew(id === undefined);
    } else {
      // 1. Check for switching between existing objects
      if (id !== undefined && !isNew && !wasCreated && id !== prevId) {
        setIdRef(id);
        load();
      }

      // 2. Switching from a newly created object to an existing one
      else if (id !== undefined && isNew && wasCreated && urlChanged) {
        setIsNew(false);
        setWasCreated(false);
        setIdRef(id);
        load();
      }

      // 3. A new object was created
      else if (id !== undefined && isNew && wasCreated) {
        setWasCreated(true);
        setUrlChanged(true);
      }

      // 4. switching from new to existing
      else if (id !== undefined && !isNew && !wasCreated) {
        setIsNew(false);
        setWasCreated(false);
        setIdRef(id);
        load();
      }

      // 4. Switching from existing to new
      else if (id === undefined && !isNew) {
        setIsNew(true);
        setWasCreated(false);
      }

      // 5. Switching from a created object back to new
      else if (id === undefined && wasCreated) {
        setIsNew(true);
        setWasCreated(false);
        setIdRef(uuid4());
      }
    }

    // Update previous ID at the end of each cycle
    setPrevId(id);
  }, [id]);

  useEffect(() => {
    if (isNew === false) {
      load();
      setIdRef(id);
    } else {
      setWasCreated(false);
      setIdRef(uuid4());
    }
  }, [isNew]);

  return {
    isNew,
    idRef,
    wasCreated,
    setWasCreated,
  };
};

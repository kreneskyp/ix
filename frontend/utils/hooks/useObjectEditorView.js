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

  // idRef changes:
  // 1. switch between existing -> load
  // 2. switch from new to saved -> don't load (it was created in place)
  // 3. switch from new to existing -> existing -> load
  // 4. switch from existing to new -> new -> don't load
  useEffect(() => {
    if (idRef === null) {
      return;
    }

    if (isNew === false) {
      load();
    }
  }, [idRef, isNew]);

  // ID change indicates:
  // 1. Switching between existing objects
  // 2. A new object was created (url changed)
  // 3. switching from existing to new blank form
  useEffect(() => {
    if (id === undefined || id === null) {
      const newId = uuid4();
      setIdRef(newId);
      setIsNew(true);
    } else {
      setIdRef(id);
      setIsNew(false);
    }
  }, [id]);

  return {
    isNew,
    idRef,
  };
};

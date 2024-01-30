import useCreateAPI from "utils/hooks/useCreateAPI";
import useUpdateAPI from "utils/hooks/useUpdateAPI";

/**
 * Hook that encapsulates both create and update APIs into a single save function.
 * @param createURL
 * @param updateURL
 * @returns {{isLoading: boolean, save: ((function(*): Promise<any|undefined>)|*)}}
 */
export const useCreateUpdateAPI = (createURL, updateURL) => {
  const {
    create,
    isLoading: isCreateLoading,
    error: createError,
  } = useCreateAPI(createURL);
  const {
    call: update,
    isLoading: isUpdateLoading,
    error: updateError,
  } = useUpdateAPI(updateURL);

  const save = async (data) => {
    if (data.id) {
      return await update(data);
    } else {
      return await create(data);
    }
  };

  return {
    save,
    error: createError?.response || updateError?.response || undefined,
    isLoading: isCreateLoading || isUpdateLoading,
  };
};

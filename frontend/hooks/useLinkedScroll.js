import React from "react";

/**
 * LinkedScroll is a custom hook that synchronizes scrolling between two
 * elements. For example, between a drawer and a scrollable box.
 *
 * It requires components be linked with refs, but otherwise it's self-contained.
 */
export const useLinkedScroll = () => {
  const targetRef = React.useRef(null);
  const sourceRef = React.useRef(null);

  // callback to update scroll position of targetRef
  const updateScroll = React.useCallback(
    (e) => {
      // Calculate isMoverOver here using mouse position and refs.
      // Done here with refs to avoid re-rendering janky scrolling
      const targetRect = targetRef.current.getBoundingClientRect();
      const sourceRect = sourceRef.current
        ? sourceRef.current.getBoundingClientRect()
        : null;

      const isOverTarget =
        e.clientX >= targetRect.left &&
        e.clientX <= targetRect.right &&
        e.clientY >= targetRect.top &&
        e.clientY <= targetRect.bottom;

      const isOverDrawer =
        sourceRect &&
        e.clientX >= sourceRect.left &&
        e.clientX <= sourceRect.right &&
        e.clientY >= sourceRect.top &&
        e.clientY <= sourceRect.bottom;

      const isMouseOver = isOverTarget && !isOverDrawer;

      if (isMouseOver && targetRef.current) {
        targetRef.current.scrollTop += e.deltaY;
      }
    },
    [targetRef, sourceRef]
  );

  // add global listener for wheel events, this decouples the wheel event capture
  // from the overlay. The overlay might need ignore all mouse events to allow buttons
  // and other elements work. (those things do work with the pass through unlike scrolling)
  React.useEffect(() => {
    window.addEventListener("wheel", updateScroll);
    return () => {
      window.removeEventListener("wheel", updateScroll);
    };
  }, []);

  return { targetRef, sourceRef };
};

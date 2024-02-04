// Helper function to create a smooth bend
const createSmoothBend = (a, b, c, borderRadius) => {
  const isHorizontal = a.y === b.y;
  const isVertical = a.x === b.x;
  const isMovingRight = b.x > a.x;
  const isMovingDown = b.y > a.y;
  const nextIsRight = c.x > b.x;
  const nextIsDown = c.y > b.y;

  let curve = "";

  if (isHorizontal) {
    // The previous segment was horizontal
    if (isMovingRight) {
      curve = `L ${b.x - borderRadius},${b.y} `; // Line up to the horizontal bend
      // Check the vertical direction after the bend
      curve += nextIsDown
        ? `Q ${b.x},${b.y} ${b.x},${b.y + borderRadius}`
        : `Q ${b.x},${b.y} ${b.x},${b.y - borderRadius}`;
    } else {
      curve = `L ${b.x + borderRadius},${b.y} `; // Line up to the horizontal bend
      // Check the vertical direction after the bend
      curve += nextIsDown
        ? `Q ${b.x},${b.y} ${b.x},${b.y + borderRadius}`
        : `Q ${b.x},${b.y} ${b.x},${b.y - borderRadius}`;
    }
  } else if (isVertical) {
    // The previous segment was vertical
    if (isMovingDown) {
      curve = `L ${b.x},${b.y - borderRadius} `; // Line up to the vertical bend
      // Check the horizontal direction after the bend
      curve += nextIsRight
        ? `Q ${b.x},${b.y} ${b.x + borderRadius},${b.y}`
        : `Q ${b.x},${b.y} ${b.x - borderRadius},${b.y}`;
    } else {
      curve = `L ${b.x},${b.y + borderRadius} `; // Line up to the vertical bend
      // Check the horizontal direction after the bend
      curve += nextIsRight
        ? `Q ${b.x},${b.y} ${b.x + borderRadius},${b.y}`
        : `Q ${b.x},${b.y} ${b.x - borderRadius},${b.y}`;
    }
  }

  return curve;
};

// Path that loops around to a node "earlier" in the graph
// a.k.a. to the left of the source.
export const getLoopPath = ({
  sourceX,
  sourceY,
  targetX,
  targetY,
  borderRadius = 5,
  offset = 20,
}) => {
  const rightOffset = offset;
  const downOffset = 160; // Adjusted for visual clarity
  const leftOffset = offset;

  // Define points for the path
  const points = [
    { x: sourceX, y: sourceY },
    { x: sourceX + rightOffset, y: sourceY },
    { x: sourceX + rightOffset, y: sourceY + downOffset },
    { x: targetX - leftOffset, y: sourceY + downOffset },
    { x: targetX - leftOffset, y: targetY },
    { x: targetX, y: targetY },
  ];

  // Generate the SVG path
  const path = points.reduce((res, point, i, arr) => {
    if (i === 0) return `M ${point.x},${point.y}`;

    // Use the custom bend function for smooth transitions
    if (i < arr.length - 1) {
      return (
        res + createSmoothBend(arr[i - 1], point, arr[i + 1], borderRadius)
      );
    } else {
      return res + ` L ${point.x},${point.y}`;
    }
  }, "");

  const labelX = (sourceX + targetX) / 2;
  const labelY = (sourceY + targetY) / 2 + downOffset / 2;
  const offsetX = labelX - sourceX;
  const offsetY = labelY - sourceY;

  return [path, labelX, labelY, offsetX, offsetY];
};

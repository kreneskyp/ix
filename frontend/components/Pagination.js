import React from "react";
import { Box, Button, Flex } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faChevronLeft,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons";

export const Pagination = ({
  hasNext,
  hasPrevious,
  pages,
  pageNumber,
  load,
  size,
}) => {
  const handleClick = (page) => {
    const offset = (page - 1) * 10;
    load({ limit: 10, offset });
  };

  return (
    <Flex justify="center" align="center">
      <Button
        isDisabled={!hasPrevious}
        onClick={() => handleClick(pageNumber - 1)}
        size="sm"
        mr={30}
      >
        <FontAwesomeIcon icon={faChevronLeft} />
      </Button>
      {pageNumber > 3 && (
        <>
          {pageNumber > 4 && (
            <Button size="sm" colorScheme="gray" mx={1} disabled>
              ...
            </Button>
          )}
        </>
      )}
      {pageNumber <= 4 && (
        <Box mx={1} width={30}>
          {" "}
        </Box>
      )}
      {Array.from({ length: Math.min(pages, 7) })
        .map((_, index) => pageNumber - 3 + index)
        .filter((page) => page > 0 && page <= pages)
        .map((page) => (
          <Button
            key={page}
            variant={page === pageNumber ? "solid" : "outline"}
            size="sm"
            colorScheme={page === pageNumber ? "blue" : "gray"}
            onClick={() => handleClick(page)}
            mx={1}
          >
            {page}
          </Button>
        ))}
      {pageNumber < pages - 2 && (
        <>
          {pageNumber < pages - 3 && (
            <Button size="sm" colorScheme="gray" mx={1} disabled>
              ...
            </Button>
          )}
        </>
      )}
      {pageNumber > pages - 4 && (
        <Box mx={1} width={30}>
          {" "}
        </Box>
      )}
      <Button
        ml={30}
        ml={30}
        isDisabled={!hasNext}
        onClick={() => handleClick(pageNumber + 1)}
        size="sm"
      >
        <FontAwesomeIcon icon={faChevronRight} />
      </Button>
    </Flex>
  );
};

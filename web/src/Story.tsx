

import React, { useState } from 'react';

import { IoArrowBackCircle } from "react-icons/io5";
import { IoArrowForwardCircle } from "react-icons/io5";

function nums(size: number) {
  return new Array(size).fill(null).map((_, i) => i)
}

function makeBar(dark: boolean) {
  return <div className={"h-1 w-12 rounded " + (dark ? "bg-black" : "bg-gray-300")}></div>
}

function Story() {
  const [page, setPage] = useState(0)

  const arrowSize = 64

  return (
    <div className="h-screen flex flex-col">
      <div className="flex flex-row justify-around px-20 py-4">
        {nums(10).map(i => {
          return (<div key={i}>{makeBar(i <= page)}</div>)
        })}
      </div>
      <div className="flex-grow">Content</div>
      <div className="flex flex-row justify-between p-8">
        <IoArrowBackCircle size={arrowSize} />
        <IoArrowForwardCircle size={arrowSize} />
      </div>
    </div>
  );
}

export default Story;



import React, { useState, useEffect } from 'react';

import {
  useParams,
} from "react-router-dom";

import axios from 'axios'

import { IoArrowBackCircle } from "react-icons/io5";
import { IoArrowForwardCircle } from "react-icons/io5";

import { HOST, Story, Page } from './shared'

function nums(size: number) {
  return new Array(size).fill(null).map((_, i) => i)
}

function makeBar(dark: boolean) {
  return <div className={"h-1 w-12 rounded " + (dark ? "bg-black" : "bg-gray-300")}></div>
}

function StoryPage() {
  const [index, setIndex] = useState(0)
  const [page, setPage] = useState<Page|undefined>(undefined)

  const { story_id } = useParams();
  console.log("Loading for story", story_id)

  const arrowSize = 64

  function loadPage(pageIndex: number) {
    axios.get(HOST + "stories/" + story_id).then(res => {
      let story = res.data
      console.log("Got story", story)
      let page = story.pages[pageIndex];
      setPage(page)
      setIndex(pageIndex)
    }).catch(err => {
      console.log("Failed to load story", err);
    })
  }

  useEffect(() => {
    loadPage(0)
  }, []);

  if (page === undefined) {
    return <div>"Loading..."</div>
  }

  return (
    <div className="h-screen flex flex-col">
      <div className="flex flex-row justify-around px-20 py-4">
        {nums(10).map(i => {
          return (<div key={i}>{makeBar(i <= index)}</div>)
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

export default StoryPage;

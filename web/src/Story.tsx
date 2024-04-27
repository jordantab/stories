

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

const TEST_PAGE_1: Page = {
  number: 0,
  title: "Google Cloud",
  text: "Data Warehousing in the Age of AI",
  type: "display",
  img_url: "",
}

const TEST_PAGE_2: Page = {
  number: 0,
  title: "",
  text: "Let's start with your email",
  type: "query",
  img_url: "",
}

function StoryPage() {
  const [index, setIndex] = useState(0)
  const [page, setPage] = useState<Page|undefined>(TEST_PAGE_2)
  const [queryResponse, setQueryResponse] = useState("")

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

  function nextPage() {
    loadPage(index + 1)
  }

  function prevPage() {
    loadPage(index - 1)
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
      <div className="flex-grow flex flex-col justify-center space-y-4 py-8 px-20">
        {
          page.type === "query" ? (
            <>
              <p className="text-2xl font-bold">{page.text}</p>
              <input value={queryResponse}
                onChange={ev => setQueryResponse(ev.target.value)} className="border rounded-lg p-3 w-1/4"
                type="text" placeholder="Type your answer here" />
            </>
          ) : (
            <>
              <h2 className="text-6xl font-bold">{page.title}</h2>
              <p className="text-2xl">{page.text}</p>
            </>
          )
        }

      </div>
      <div className="flex flex-row justify-between p-8">
        <IoArrowBackCircle size={arrowSize} onClick={() => prevPage()} />
        <IoArrowForwardCircle size={arrowSize} onClick={() => nextPage()} />
      </div>
    </div>
  );
}

export default StoryPage;

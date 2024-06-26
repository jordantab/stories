import React, { useState, useEffect } from "react";

import { Link } from "react-router-dom";

import axios from "axios";

import { useDropzone } from "react-dropzone";

import { MdOutlineShare } from "react-icons/md";
import { HiOutlineTrash } from "react-icons/hi";
import { LuDownload } from "react-icons/lu";
import { MdOutlineFileUpload } from "react-icons/md";

import { HOST, Story, Page } from "./shared";

function Admin() {
  const [name, setName] = useState("");
  const [tagline, setTagline] = useState("");
  const [items, setItems] = useState<Story[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [files, setFiles] = useState<any>([]);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      setFiles(acceptedFiles);
      console.log(acceptedFiles);
    },
  });

  function fetchStories() {
    axios
      .get(HOST + "stories")
      .then((res) => {
        console.log("Got stories list", res.data);
        setItems(res.data);
      })
      .catch((err) => {
        console.log("ERR:", err);
      });
  }

  useEffect(() => {
    console.log("Component loaded");
    fetchStories();
    return () => {
      console.log("Component unmounted");
    };
  }, []);

  function createStory() {
    const formData = new FormData();
    // files.forEach((file: any, index: number) => {
    //   formData.append(`file-${index}`, file);
    // });
    formData.append("file", files[0]);
    formData.append("name", name);
    formData.append("tagline", tagline);

    const config = {
      headers: {
        "content-type": "multipart/form-data",
      },
    };

    axios
      .post(HOST + "stories", formData, config)
      .then((response) => {
        console.log(response.data);
        setShowModal(false);
        console.log("Upload complete");
        fetchStories();
      })
      .catch((error) => {
        console.error("Error uploading files: ", error);
      });
  }

  function Modal() {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex justify-center items-center">
        <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col space-y-2">
          <h2 className="text-3xl font-bold mb-4">New Story</h2>
          <p className="mb-4 text-gray-500">
            Story will be automatically generated with GenAI from any of your
            existing white papers or docs
          </p>

          <p className="text-sm">Pick a name</p>
          <input
            className="border rounded p-1"
            type="text"
            placeholder="Type your name here"
            value={name}
            onChange={(ev) => setName(ev.target.value)}
          />

          <p className="text-sm">Pick a tagline</p>
          <input
            className="border rounded p-1"
            type="text"
            placeholder="Type your tagline here"
            value={tagline}
            onChange={(ev) => setTagline(ev.target.value)}
          />

          <p className="text-sm">Upload your pdf</p>
          <div
            {...getRootProps({
              className:
                "dropzone border border-gray-300 rounded-lg p-10 text-center",
            })}
          >
            <input {...getInputProps()} />
            <div className="flex flex-row justify-center items-center space-x-2">
              <MdOutlineFileUpload size={18} />
              <p>Drop files here</p>
            </div>
            {files.map((f: any) => (
              <div key={f.name}>{f.name}</div>
            ))}
          </div>
          <div className="flex flex-row justify-end pt-4 space-x-4">
            <button
              className="bg-gray-100 hover:bg-gray-300 border font-bold py-2 px-4 rounded"
              onClick={() => setShowModal(false)}
            >
              Cancel
            </button>
            <button
              className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
              onClick={() => createStory()}
            >
              Create
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="p-4 flex flex-row justify-between items-center border-b">
        <div className="text-purple-500 font-bold">stories</div>
        <button
          className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-1 px-3 rounded"
          onClick={() => setShowModal(true)}
        >
          + Create Story
        </button>
      </div>
      <div className="flex-1 py-10 px-20 space-y-4">
        <h1 className="text-5xl">Your Stories</h1>
        {items.map((item) => story(item))}
      </div>
      {showModal ? Modal() : undefined}
    </div>
  );
}

function story(story: Story) {
  function downloadLeads() {
    axios
      .get(HOST + "leads")
      .then((res) => {
        console.log("Got leads list", res.data);
        let filtered: any[] = [];
        for (let i = 0; i < res.data.length; i++) {
          let lead = res.data[i];
          if (lead.story_id === story._id) {
            filtered.push(lead);
          }
        }
        console.log("Filtered list", filtered);
        const element = document.createElement("a");
        const file = new Blob([JSON.stringify(filtered)], {
          type: "text/json",
        });
        element.href = URL.createObjectURL(file);
        element.download = story._id + "-leads.json";
        document.body.appendChild(element); // Required for this to work in FireFox
        element.click();
        console.log("Leads list should be downloaded now");
      })
      .catch((err) => {
        console.log("ERR:", err);
      });
  }

  return (
    <div
      key={story._id}
      className="w-full border p-4 rounded flex flex-row justify-between items-center"
    >
      <div className="flex flex-col">
        <div className="text-lg font-bold">{story.name}</div>
        <div className="text-md">{story.tagline}</div>
      </div>
      <div className="flex flex-row space-x-4">
        <button
          className="border rounded p-2 flex flex-row space-x-2"
          onClick={() => downloadLeads()}
        >
          <LuDownload size={24} />
          <div className="font-bold">Download leads</div>
        </button>
        <Link to={"/story/" + story._id}>
          <button className="border rounded p-2">
            <MdOutlineShare size={24} />
          </button>
        </Link>
        <button className="border rounded p-2">
          <HiOutlineTrash size={24} />
        </button>
      </div>
    </div>
  );
}

export default Admin;

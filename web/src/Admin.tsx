

import React, { useState } from 'react';

import { useDropzone } from 'react-dropzone';

import { MdOutlineShare } from "react-icons/md";
import { HiOutlineTrash } from "react-icons/hi";
import { LuDownload } from "react-icons/lu";

interface Story {
  title: string,
  subtitle: string,
}

const DEFAULT_ITEMS = [
  {
    title: "The Big Book of Generative AI",
    subtitle: "White Paper",
  },
  {
    title: "MLOps for Dummies",
    subtitle: "E-Book",
  },
]

function Admin() {
  const [items, setItems] = useState<Story[]>(DEFAULT_ITEMS)
  const [showModal, setShowModal] = useState(true)
  return (
    <div className="flex flex-col h-screen">
      <div className="p-4 flex flex-row justify-between items-center border-b">
        <div className="text-purple-500 font-bold">stories</div>
        <button className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-1 px-3 rounded">+ Create Story</button>
      </div>
      <div className="flex-1 py-10 px-20 space-y-4">
        <h1 className="text-5xl">Your Stories</h1>
        {items.map(item => story(item))}
      </div>
      {showModal ? Modal() : undefined}
    </div>
  );
}

function story(story: Story) {
  return (
    <div className="w-full border p-4 rounded flex flex-row justify-between items-center">
      <div className="flex flex-col">
        <div className="text-lg font-bold">{story.title}</div>
        <div className="text-md">{story.subtitle}</div>
      </div>
      <div className="flex flex-row space-x-4">
        <button className="border rounded p-2 flex flex-row space-x-2"><LuDownload size={24} /><div className="font-bold">Download leads</div></button>
        <button className="border rounded p-2"><MdOutlineShare size={24} /></button>
        <button className="border rounded p-2"><HiOutlineTrash size={24} /></button>
      </div>
    </div>
  )
}

function Modal() {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      console.log(acceptedFiles);
    }
  });
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-3xl font-bold mb-4">New Story</h2>
          <p className="mb-4 text-gray-500">Story will be automatically generated with GenAI from any of your existing white papers or docs</p>
          <p className="text-sm">Upload your pdf</p>
          <div {...getRootProps({ className: 'dropzone border-dashed border-4 border-gray-300 p-10 text-center' })}>
              <input {...getInputProps()} />
              <p>Drag 'n' drop some files here, or click to select files</p>
            </div>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              Close Modal
          </button>
      </div>
  </div>
  )
}

export default Admin;

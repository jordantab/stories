import React from 'react';

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import Admin from './Admin'
import Story from './Story'

const router = createBrowserRouter([
  {
    path: "/",
    element: <div>Hello world!</div>,
  },
  {
    path: "/admin",
    element: <Admin/>,
  },
  {
    path: "/story/:story_id",
    element: <Story/>,
  },
]);

function App() {
  return (
    <div className="App">
      <RouterProvider router={router} />
    </div>
  );
}

export default App;

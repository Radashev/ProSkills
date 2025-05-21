import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router";
import "./App.css";
import { routes } from "./routes";

const App: React.FC = () => {
  const router = createBrowserRouter(routes);
  return <RouterProvider router={router} />;
};

export default App;

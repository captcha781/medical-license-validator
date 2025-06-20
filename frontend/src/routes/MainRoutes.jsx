import Loadable from "../components/Loadable";
import RouteCondition from "../helper/RouteCondition";
import { lazy } from "react";
import { Navigate } from "react-router-dom";

const Signup = Loadable(lazy(() => import("../pages/Signup")));
const Signin = Loadable(lazy(() => import("../pages/Signin")));
const Dashboard = Loadable(lazy(() => import("../pages/Dashboard")));

const MainRoutes = [
  {
    path: "/",
    element: <Navigate to="/signin" replace />,
  },
  {
    path: "/signup",
    element: (
      <RouteCondition type="auth">
        <Signup />
      </RouteCondition>
    ),
  },
  {
    path: "/signin",
    element: (
      <RouteCondition type="auth">
        <Signin />
      </RouteCondition>
    ),
  },
  {
    path: "/dashboard",
    element: (
      <RouteCondition type="private">
        <Dashboard />
      </RouteCondition>
    ),
  },
];

export default MainRoutes;

import Loadable from "../components/Loadable";
import RouteCondition from "../helper/RouteCondition";
import { lazy } from "react";
import { Navigate } from "react-router-dom";

const Signup = Loadable(lazy(() => import("../pages/Signup")));
const Signin = Loadable(lazy(() => import("../pages/Signin")));
const Dashboard = Loadable(lazy(() => import("../pages/Dashboard")));
const ReportView = Loadable(lazy(() => import("../pages/ReportView")));

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
  {
    path: "/report/:report_id",
    element: (
      <RouteCondition type="private">
        <ReportView />
      </RouteCondition>
    ),
  },
  {
    path: "*",
    element: (
      <div className="flex items-center justify-center h-screen">
        <h1 className="text-3xl font-bold">404 - Page Not Found</h1>
      </div>
    )
  }
];

export default MainRoutes;

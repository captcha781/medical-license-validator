import React, { useCallback, useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import moment from "moment";
import { useDispatch } from "react-redux";
import { revokeAuth } from "../redux/slices/auth.slice";
import config from "../config";

const ViewReport = () => {
  const { report_id } = useParams();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const runOnce = useRef(false);
  const dispatch = useDispatch();

  const fetchReport = useCallback(async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const response = await axios.get(
        `/report/${report_id}`,
        {
          baseURL: config.API_URL,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.success) {
        setReport({...response.data.result.result, created_at: response.data.result.created_at});
      } else {
        setError("Failed to fetch report.");
      }
    } catch (err) {
      console.log(err);
      setError("Failed to fetch report.");
    }
  }, [report_id]);

  useEffect(() => {
    if (!runOnce.current) {
      runOnce.current = true;
      fetchReport();
    }
  }, [fetchReport]);

  const formatClassifierResult = (result) => {
    return result
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    dispatch(revokeAuth({}));
  };

    console.log(report)

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md flex flex-col justify-between">
        <div>
          <div className="text-2xl font-bold text-blue-600 px-6 py-4 border-b">
            MedScore
          </div>
          <nav className="px-6 py-4 border-b">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Navigation
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  to="/dashboard"
                  className="text-blue-600 hover:underline text-sm"
                >
                  Go to Dashboard
                </Link>
              </li>
            </ul>
          </nav>
        </div>
        <div className="px-6 py-4 border-t">
          <a
            href="#"
            className="text-gray-500 hover:text-blue-600 text-sm font-medium"
          >
            Privacy Policy
          </a>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Navbar */}
        <nav className="bg-white shadow-md px-6 py-5 flex justify-end items-center">
          <div className="space-x-4">
            <a
              href="#"
              onClick={handleLogout}
              className="text-gray-700 hover:text-blue-600 font-medium"
            >
              Logout
            </a>
          </div>
        </nav>

        {/* Report View */}
        <div className="flex items-center justify-center px-4 py-10">
          <div className="bg-white p-8 rounded-xl shadow-md w-3/5">
            {error ? (
              <p className="text-red-600 text-center">{error}</p>
            ) : !report ? (
              <p className="text-center text-gray-600">Loading report...</p>
            ) : (
              <>
                <h2 className="text-xl font-semibold text-gray-800 mb-6 text-center">
                  Report Details - {report_id}
                </h2>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700">
                      Created At:
                    </h3>
                    <p className="text-gray-800">
                      {moment(new Date(report.created_at)).format(
                        "MMMM Do YYYY, h:mm A"
                      )}
                    </p>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700">
                      Classifier Result:
                    </h3>
                    <p className="text-gray-800">
                      {formatClassifierResult(report.classifier_result)}
                    </p>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700">
                      Credibility Score:
                    </h3>
                    <p className="text-blue-700 font-bold text-lg">
                      {report.credebility_result.credibility_score}/100
                    </p>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700">
                      Summary:
                    </h3>
                    <p className="text-gray-800">
                      {report.credebility_result.summary}
                    </p>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700">
                      Flag:
                    </h3>
                    <p
                      className={`font-bold ${
                        report.credebility_result.flag === "red"
                          ? "text-red-600"
                          : report.credebility_result.flag === "yellow"
                          ? "text-yellow-600"
                          : "text-green-600"
                      }`}
                    >
                      {report.credebility_result.flag.toUpperCase()}
                    </p>
                  </div>
                  {report.credebility_result.discrepancies.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700">
                        Discrepancies:
                      </h3>
                      <ul className="list-disc pl-5 text-gray-800">
                        {report.credebility_result.discrepancies.map(
                          (item, index) => (
                            <li key={index}>{item}</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ViewReport;

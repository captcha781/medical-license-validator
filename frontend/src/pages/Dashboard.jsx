import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import { revokeAuth } from "../redux/slices/auth.slice";
import { useDispatch } from "react-redux";
import moment from "moment";
import { Link } from "react-router-dom";
import config from "../config";

const UploadDocuments = () => {
  const [resume, setResume] = useState(null);
  const [credential, setCredential] = useState(null);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();
  const runOnce = useRef(false);
  const [result, setResult] = useState({
    classifier_result: "",
    credebility_result: {
      credibility_score: 0,
      summary: "",
      flag: "",
      discrepancies: [],
    },
  });

  const [reports, setReports] = useState([]);

  const formatClassifierResult = (result) => {
    let splitResult = result.split("_");
    let formattedResult = splitResult
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
    return formattedResult;
  };

  const getStatusDotColor = (status) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "pending":
        return "bg-yellow-500";
      case "failed":
        return "bg-red-500";
      default:
        return "bg-gray-400";
    }
  };

  const retrieveReportHistory = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const response = await axios.get("/report-history-list", {
        baseURL: config.API_URL,
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.data.success) {
        setReports(response.data.result);
      }
    } catch (error) {
      console.log(error);
      alert("Could not load Report History Data");
    }
  };

  useEffect(() => {
    if (!runOnce.current) {
      runOnce.current = true;
      retrieveReportHistory();
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resume || !credential) {
      setMessage("Please upload both documents.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("credential", credential);

    try {
      setIsLoading(true);
      const token = localStorage.getItem("accessToken");
      const response = await axios.post("/run-agent", formData, {
        baseURL: config.API_URL,
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });
      setMessage("Upload successful!");
      setIsLoading(false);
      if (response.data.success) {
        setResult(response.data.result);
      }
      await retrieveReportHistory();
    } catch (error) {
      setIsLoading(false);
      console.error("Upload failed:", error);
      setMessage("Upload failed. Please try again.");
    }
  };

  const handleReset = () => {
    setResume(null);
    setCredential(null);
    setMessage("");
    setResult({
      classifier_result: "",
      credebility_result: {
        credibility_score: 0,
        summary: "",
        flag: "",
        discrepancies: [],
      },
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    dispatch(revokeAuth({}));
  };
console.log(reports)
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
              Reports History
            </h3>
            <ul className="space-y-3 max-h-72 overflow-y-auto pr-2">
              {reports.map((report) => (
                <Link
                  to={`/report/${report.report_id}`}
                  key={report.report_id}
                  className="flex items-center space-x-2"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {report.report_id}
                    </p>
                    <p className="text-xs text-gray-500">
                      {moment.utc(report.created_at).local().fromNow()}
                    </p>
                  </div>
                  <span
                    className={`h-3 w-3 rounded-full ${getStatusDotColor(
                      report.status
                    )}`}
                  ></span>
                </Link>
              ))}
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

        {/* Upload Form / Result */}
        <div className="flex items-center justify-center px-4 py-10">
          <div className="bg-white p-8 rounded-xl shadow-md  w-3/5">
            <h2 className="text-xl font-semibold text-gray-800 mb-6 text-center">
              {result.classifier_result
                ? "Document Analysis Result"
                : "Upload Documents"}
            </h2>

            {!result.classifier_result ? (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Resume (PDF/Image)
                  </label>
                  <input
                    type="file"
                    accept=".pdf, image/*"
                    onChange={(e) => setResume(e.target.files[0])}
                    className="w-full"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Credential (PDF/Image)
                  </label>
                  <input
                    type="file"
                    accept=".pdf, image/*"
                    onChange={(e) => setCredential(e.target.files[0])}
                    className="w-full"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className={`w-full flex items-center justify-center bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition ${
                    isLoading ? "opacity-70 cursor-not-allowed" : ""
                  }`}
                >
                  {isLoading ? (
                    <>
                      <svg
                        className="animate-spin h-5 w-5 mr-2 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8v4l3.5-3.5L12 0v4a8 8 0 00-8 8z"
                        />
                      </svg>
                      Uploading...
                    </>
                  ) : (
                    "Submit"
                  )}
                </button>

                {message && (
                  <p className="mt-4 text-center text-sm text-gray-700">
                    {message}
                  </p>
                )}
              </form>
            ) : (
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700">
                    Classifier Result:
                  </h3>
                  <p className="text-gray-800">
                    {formatClassifierResult(result.classifier_result)}
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-700">
                    Credibility Score:
                  </h3>
                  <p className="text-blue-700 font-bold text-lg">
                    {result.credebility_result.credibility_score}/100
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-700">
                    Summary:
                  </h3>
                  <p className="text-gray-800">
                    {result.credebility_result.summary}
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-700">Flag:</h3>
                  <p
                    className={`font-bold ${
                      result.credebility_result.flag === "red"
                        ? "text-red-600"
                        : result.credebility_result.flag === "yellow"
                        ? "text-yellow-600"
                        : "text-green-600"
                    }`}
                  >
                    {result.credebility_result.flag.toUpperCase()}
                  </p>
                </div>
                {result.credebility_result.discrepancies.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700">
                      Discrepancies:
                    </h3>
                    <ul className="list-disc pl-5 text-gray-800">
                      {result.credebility_result.discrepancies.map(
                        (item, index) => (
                          <li key={index}>{item}</li>
                        )
                      )}
                    </ul>
                  </div>
                )}
                <button
                  onClick={handleReset}
                  className="mt-4 w-full bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 transition"
                >
                  Upload Another
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadDocuments;

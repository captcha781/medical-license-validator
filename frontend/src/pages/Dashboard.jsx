import React, { useState } from "react";
import axios from "axios";

const UploadDocuments = () => {
  const [resume, setResume] = useState(null);
  const [credential, setCredential] = useState(null);
  const [message, setMessage] = useState("");
  const [result, setResult] = useState({
    classifier_result: "",
    credebility_result: {
      credibility_score: 0,
      summary: "",
      flag: "",
      discrepancies: [],
    },
  });

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
      const token = localStorage.getItem("access_token");
      const response = await axios.post(
        "http://localhost:5000/api/run-agent",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMessage("Upload successful!");
      if (response.data.success) {
        setResult(response.data.result);
      }
    } catch (error) {
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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="bg-white p-8 rounded-xl shadow-md max-w-md w-full">
        <h2 className="text-xl font-semibold text-gray-800 mb-6 text-center">
          {result.classifier_result ? "Document Analysis Result" : "Upload Documents"}
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
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Submit
            </button>
            {message && (
              <p className="mt-4 text-center text-sm text-gray-700">{message}</p>
            )}
          </form>
        ) : (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-700">Classifier Result:</h3>
              <p className="text-gray-800">{result.classifier_result}</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-700">Credibility Score:</h3>
              <p className="text-blue-700 font-bold text-lg">
                {result.credebility_result.credibility_score}%
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-700">Summary:</h3>
              <p className="text-gray-800">{result.credebility_result.summary}</p>
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
                <h3 className="text-sm font-semibold text-gray-700">Discrepancies:</h3>
                <ul className="list-disc pl-5 text-gray-800">
                  {result.credebility_result.discrepancies.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
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
  );
};

export default UploadDocuments;

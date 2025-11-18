import { useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";
import AdminPage from "./pages/AdminPage";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="App-header bg-white shadow-md py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <img 
              src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4" 
              alt="Logo"
              className="w-24 h-24 rounded-full shadow-lg"
            />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            JobDiva-GoTo Bridge Service
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Seamless integration between JobDiva ATS and GoTo Connect
          </p>
          
          <div className="flex justify-center gap-4">
            <Link 
              to="/admin"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition shadow-lg hover:shadow-xl"
              data-testid="admin-dashboard-link"
            >
              Go to Admin Dashboard
            </Link>
            <a 
              href="https://emergent.sh" 
              target="_blank" 
              rel="noopener noreferrer"
              className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-3 rounded-lg font-semibold transition"
            >
              Learn More
            </a>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-2">📞</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Call Integration</h3>
              <p className="text-sm text-gray-600">
                Initiate calls from JobDiva directly through GoTo Connect with automatic candidate note logging.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-2">💬</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">SMS Messaging</h3>
              <p className="text-sm text-gray-600">
                Send SMS messages to candidates with full tracking and JobDiva note creation.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-2">📊</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Interaction History</h3>
              <p className="text-sm text-gray-600">
                Complete audit trail of all communications between recruiters and candidates.
              </p>
            </div>
          </div>

          <div className="mt-12 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              ⚠️ Development Mode
            </h3>
            <p className="text-sm text-yellow-800">
              This application is currently using <strong>mocked APIs</strong> for GoTo Connect and JobDiva. 
              Replace service implementations with real API credentials when ready for production.
            </p>
          </div>
        </div>
      </header>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;

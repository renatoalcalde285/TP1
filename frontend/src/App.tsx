import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import UploadPage from "./pages/UploadPage";
import ProcessingPage from "./pages/ProcessingPage";
import ReviewPage from "./pages/ReviewPage";
import AuditDashboardPage from "./pages/AuditDashboardPage";


function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<LoginPage />}
        />

        <Route
          path="/upload"
          element={<UploadPage />}
        />

        <Route
          path="/processing/:documentId"
          element={<ProcessingPage />}
        />

        <Route
          path="/review/:documentId"
          element={<ReviewPage />}
        />

        <Route
          path="/audit"
          element={<AuditDashboardPage />}
        />

      </Routes>

    </BrowserRouter>

  );
}

export default App;
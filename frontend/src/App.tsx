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
import AuditSuccessPage from "./pages/AuditSuccessPage";
import ProcessingBatchPage from "./pages/ProcessingBatchPage";


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

        <Route
          path="/audit-success/:documentId"
          element={<AuditSuccessPage />}
        />

        <Route
          path="/processing-batch"
          element={
            <ProcessingBatchPage />
          }
        />

      </Routes>

    </BrowserRouter>

  );
}

export default App;
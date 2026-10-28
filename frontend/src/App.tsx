import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import UploadPage from "./pages/UploadPage";
import ProcessingPage from "./pages/ProcessingPage";

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

      </Routes>

    </BrowserRouter>

  );
}

export default App;
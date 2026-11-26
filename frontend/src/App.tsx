import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { AdminRoute } from "./components/AdminRoute";
import { EnrollPage } from "./pages/admin/EnrollPage";
import { ProgramDetailPage } from "./pages/admin/ProgramDetailPage";
import { ProgramsPage } from "./pages/admin/ProgramsPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { SetPasswordPage } from "./pages/SetPasswordPage";
import "./App.css";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/set-password" element={<SetPasswordPage />} />
          <Route
            path="/admin/programs"
            element={
              <AdminRoute>
                <ProgramsPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/programs/:programId"
            element={
              <AdminRoute>
                <ProgramDetailPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/enroll"
            element={
              <AdminRoute>
                <EnrollPage />
              </AdminRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
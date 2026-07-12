import { BrowserRouter, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import LeadDetail from "./pages/LeadDetail";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <div
        style={{
          minHeight: "100vh",
          width: "100%",
          background: "#060b14",
          backgroundImage:
            "radial-gradient(ellipse at 20% 50%, #0d1f1433 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, #0a1a2a22 0%, transparent 50%)",
          fontFamily: "'Courier New', 'Consolas', ui-monospace, monospace",
        }}
      >
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/leads/:id" element={<LeadDetail />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

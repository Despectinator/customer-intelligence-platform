import { Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import CustomerDetails from "./pages/CustomerDetails";
import Transactions from "./pages/Transactions";
import Analytics from "./pages/Analytics";
import Projects from "./pages/Projects";
import Upload from "./pages/Upload";
import Settings from "./pages/Settings";
import ProtectedRoute from "./components/ProtectedRoute";
import AppShell from "./components/layout/AppShell";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/customers" element={<Customers />} />
          <Route
            path="/projects/:projectId/customers"
            element={<Customers />}
          />
          <Route
            path="/projects/:projectId/customers/:customerId"
            element={<CustomerDetails />}
          />
          <Route
            path="/projects/:projectId/customers/:customerId/transactions"
            element={<Transactions />}
          />
          <Route path="/projects/:projectId/analytics" element={<Analytics />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:projectId/upload" element={<Upload />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;

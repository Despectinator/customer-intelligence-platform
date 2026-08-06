import {
  BarChart3,
  FolderKanban,
  LayoutDashboard,
  Settings,
  Upload,
  Users,
} from "lucide-react";

export const navigation = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Customers", path: "/customers", icon: Users },
  { label: "Projects", path: "/projects", icon: FolderKanban },
  { label: "Analytics", path: "/analytics", icon: BarChart3 },
  { label: "Upload CSV", path: "/upload", icon: Upload },
  { label: "Settings", path: "/settings", icon: Settings },
];

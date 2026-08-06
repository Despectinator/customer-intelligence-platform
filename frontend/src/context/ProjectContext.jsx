import { useState } from "react";
import { ProjectContext } from "./projectContextStore";

export function ProjectProvider({ children }) {
  const [currentProject, setCurrentProject] = useState(null);

  return (
    <ProjectContext.Provider value={{ currentProject, setCurrentProject }}>
      {children}
    </ProjectContext.Provider>
  );
}

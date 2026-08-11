import { useState } from "react";
import { ProjectContext } from "./projectContextStore";

const STORAGE_KEY = "currentProject";

export function ProjectProvider({ children }) {
  const [currentProject, setCurrentProjectState] = useState(() => {
    try {
      const savedProject = localStorage.getItem(STORAGE_KEY);
      return savedProject ? JSON.parse(savedProject) : null;
    } catch (error) {
      console.error("Could not restore current project:", error);
      return null;
    }
  });

  const setCurrentProject = (project) => {
    setCurrentProjectState(project);

    if (project) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(project));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  return (
    <ProjectContext.Provider value={{ currentProject, setCurrentProject }}>
      {children}
    </ProjectContext.Provider>
  );
}

import { useEffect, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { ProjectContext } from "./projectContextStore";

const LEGACY_STORAGE_KEY = "currentProject";

function getStorageKey(userId) {
  return `currentProject:${userId}`;
}

export function ProjectProvider({ children }) {
  const { user } = useAuth();
  const [projectsByUser, setProjectsByUser] = useState({});

  useEffect(() => {
    // Remove the old global key so it cannot be restored for another user.
    localStorage.removeItem(LEGACY_STORAGE_KEY);
  }, []);

  let restoredProject = null;

  if (user?.id && !Object.prototype.hasOwnProperty.call(projectsByUser, user.id)) {
    try {
      const savedProject = localStorage.getItem(getStorageKey(user.id));
      restoredProject = savedProject ? JSON.parse(savedProject) : null;
    } catch (error) {
      console.error("Could not restore current project:", error);
    }
  }

  const currentProject = user?.id
    ? projectsByUser[user.id] ?? restoredProject
    : null;

  const setCurrentProject = (project) => {
    if (!user?.id) return;

    const storageKey = getStorageKey(user.id);

    setProjectsByUser((current) => ({
      ...current,
      [user.id]: project,
    }));

    if (project) {
      localStorage.setItem(storageKey, JSON.stringify(project));
    } else {
      localStorage.removeItem(storageKey);
    }
  };

  return (
    <ProjectContext.Provider value={{ currentProject, setCurrentProject }}>
      {children}
    </ProjectContext.Provider>
  );
}

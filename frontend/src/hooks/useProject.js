import { useContext } from "react";
import { ProjectContext } from "../context/projectContextStore";

export function useProject() {
  return useContext(ProjectContext);
}

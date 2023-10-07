import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

export function AgentNewRedirect() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate(`/chains/new`);
  }, [navigate]);

  return null;
}

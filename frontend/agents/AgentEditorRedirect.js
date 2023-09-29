import { useParams, useNavigate } from "react-router-dom";
import { useEffect } from "react";

export function AgentEditorRedirect() {
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    navigate(`/chain/${id}`);
  }, [id, navigate]);

  return null;
}

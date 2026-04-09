const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:7001";
import { useAuthStore } from "../../store/auth-store";

/**
 * Deploy HTML code to the server and return the deployment URL.
 * @param code - The HTML code to deploy
 * @param title - Optional title for the deployment
 * @returns Promise with the deployment URL and ID
 */
export async function deployToServer(
  code: string,
  title?: string
): Promise<{ id: string; url: string }> {
  if (!code || !code.trim()) {
    throw new Error("Code cannot be empty");
  }

  const authHeaders = useAuthStore.getState().getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/api/deploy`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
    },
    body: JSON.stringify({
      code,
      title: title || "",
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Deployment failed: ${response.statusText}`);
  }

  const data = await response.json();
  return {
    id: data.id,
    url: data.url,
  };
}

/**
 * Check if a deployment exists and get its metadata.
 * @param deployId - The deployment ID
 * @returns Promise with deployment status
 */
export async function getDeploymentStatus(deployId: string): Promise<{
  id: string;
  exists: boolean;
  url: string;
  size_bytes: number;
  created_at: number;
}> {
  const response = await fetch(`${API_BASE_URL}/api/deploy/${deployId}/status`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to get status: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Download the generated code as an HTML file (original functionality).
 * @param code - The HTML code to download
 */
export const deploy = (code: string) => {
  // Create a blob from the generated code
  const blob = new Blob([code], { type: "text/html" });
  const url = URL.createObjectURL(blob);

  // Create an anchor element and set properties for download
  const a = document.createElement("a");
  a.href = url;
  a.download = "index.html"; // Set the file name for download
  document.body.appendChild(a); // Append to the document
  a.click(); // Programmatically click the anchor to trigger download

  // Clean up by removing the anchor and revoking the Blob URL
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

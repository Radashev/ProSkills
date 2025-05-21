import { assignmentFilesApi } from "../api/files";
import { message } from "antd";

export const handleFileDownload = async (fileKey: string, filename: string) => {
  try {
    const response = await assignmentFilesApi.download(fileKey);
    const blob = new Blob([response.data], {
      type: response.headers["content-type"],
    });

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = filename || fileKey.split("/").pop() || "downloaded-file";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error downloading file:", error);
    message.error("Failed to download file");
  }
};

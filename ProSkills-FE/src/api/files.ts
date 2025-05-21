import api from ".";

const FILES_BASE_URL = "/file-storage";

export const assignmentFilesApi = {
  getSubmissionsByCourse: async (courseId: string, studentId: string) =>
    await api.get(
      `${FILES_BASE_URL}/course/${courseId}/submissions?student_id=${studentId}`
    ),
  download: async (fileKey: string) =>
    await api.get(`${FILES_BASE_URL}/download/${fileKey}`),
  delete: async (fileKey: string) =>
    await api.delete(`${FILES_BASE_URL}/${fileKey}`),
};

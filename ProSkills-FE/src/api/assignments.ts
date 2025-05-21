import api from ".";

const ASSIGNMENTS_BASE_URL = "/courses";

export const assignmentsApi = {
  getAllBySection: async (courseId: string, sectionId: string) =>
    await api.get(
      `${ASSIGNMENTS_BASE_URL}/${courseId}/assignments?section_id=${sectionId}`
    ),
  getById: async (courseId: string, assignmentId: string) =>
    await api.get(
      `${ASSIGNMENTS_BASE_URL}/${courseId}/assignments/${assignmentId}`
    ),
  create: async (courseId: string, formData: FormData) =>
    await api.post(
      `${ASSIGNMENTS_BASE_URL}/${courseId}/assignments/with/file`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    ),
  update: async (courseId: string, assignmentId: string, formData: FormData) =>
    await api.put(
      `${ASSIGNMENTS_BASE_URL}/${courseId}/assignments/${assignmentId}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    ),
  delete: async (courseId: string, assignmentId: string) =>
    await api.delete(
      `${ASSIGNMENTS_BASE_URL}/${courseId}/assignments/${assignmentId}`
    ),
};

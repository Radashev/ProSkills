import api from ".";
import { CourseSection, CreateUpdateCourseSection } from "../models/Course";

const SECTIONS_BASE_URL = "/sections";

export const courseSectionsApi = {
  getAllByCourse: async (courseId: string) =>
    api.get(`${SECTIONS_BASE_URL}/course/${courseId}`),
  getById: async (sectionId: string) =>
    api.get(`${SECTIONS_BASE_URL}/${sectionId}`),
  create: async (courseId: string, body: CreateUpdateCourseSection) =>
    await api.post(`${SECTIONS_BASE_URL}?course_id=${courseId}`, body),
  update: async (sectionId: string, body: CreateUpdateCourseSection) =>
    await api.put(`${SECTIONS_BASE_URL}/${sectionId}`, body),
  delete: async (sectionId: string) =>
    await api.delete(`${SECTIONS_BASE_URL}/${sectionId}`),
};

import { create } from "zustand";
import { CourseAssignment } from "../models/Course";
import { assignmentsApi } from "../api/assignments";

interface AssignmentsState {
  assignments: CourseAssignment[];
  loading: boolean;
  currentEditingAssignment: CourseAssignment | null;
  isModalVisible: boolean;
  percentDone: number;
  currentSectionId: number | null;
  fetchAssignments: (courseId: string, sectionId: number) => Promise<void>;
  addAssignment: (courseId: string, formData: FormData) => Promise<void>;
  editAssignment: (
    courseId: string,
    assignmentId: number,
    formData: FormData
  ) => Promise<void>;
  deleteAssignment: (courseId: string, id: number) => void;
  showAddModal: (sectionId: number) => void;
  showEditModal: (assignment: CourseAssignment) => void;
  hideModal: () => void;
  increasePercentDone: () => void;
}

export const useAssignmentsStore = create<AssignmentsState>((set, get) => ({
  assignments: [],
  loading: false,
  currentEditingAssignment: null,
  isModalVisible: false,
  percentDone: 0,
  currentSectionId: null,

  fetchAssignments: async (courseId: string, sectionId: number) => {
    set({ loading: true });
    try {
      const validSectionId = Number(sectionId);
      if (isNaN(validSectionId)) {
        throw new Error("Invalid sectionId");
      }

      const response = await assignmentsApi.getAllBySection(
        courseId,
        validSectionId.toString()
      );
      set({ assignments: response.data, loading: false });
    } catch (error) {
      console.error("Error fetching assignments:", error);
      set({ loading: false });
    }
  },
  addAssignment: async (courseId: string, formData: FormData) => {
    try {
      const response = await assignmentsApi.create(courseId, formData);

      if (response.status === 201) {
        const newAssignment = response.data;
        set({ assignments: [...get().assignments, newAssignment] });
      }
    } catch (error) {
      console.error("Error adding assignment:", error);
      throw error;
    }
  },

  editAssignment: async (
    courseId: string,
    assignmentId: number,
    formData: FormData
  ) => {
    try {
      const response = await assignmentsApi.update(
        courseId,
        String(assignmentId),
        formData
      );

      if (response.status === 200) {
        set({
          assignments: get().assignments.map((a) =>
            a.id === assignmentId ? response.data : a
          ),
        });
      }
    } catch (error) {
      console.error("Error updating assignment:", error);
      throw error;
    }
  },

  deleteAssignment: async (courseId: string, id: number) => {
    try {
      const response = await assignmentsApi.delete(courseId, String(id));

      if (response.status === 200) {
        set({
          assignments: get().assignments.filter((a) => a.id !== id),
        });
      }
    } catch (error) {
      console.error("Error deleting assignment:", error);
      throw error;
    }
  },

  showAddModal: (sectionId: number) => {
    set({
      currentEditingAssignment: null,
      isModalVisible: true,
      currentSectionId: sectionId,
    });
  },

  showEditModal: (assignment: CourseAssignment) => {
    set({ currentEditingAssignment: assignment, isModalVisible: true });
  },

  hideModal: () => {
    set({
      isModalVisible: false,
      currentSectionId: null,
    });
  },

  increasePercentDone: () => {
    set((state) => {
      const newPercent = state.percentDone + 50;
      return { percentDone: newPercent > 100 ? 100 : newPercent };
    });
  },
}));

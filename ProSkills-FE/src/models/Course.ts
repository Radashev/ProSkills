import { ButtonProps } from "antd";
import { NotificationInstance } from "antd/es/notification/interface";
import { ReactNode } from "react";

export interface GetCourse {
  id: number;
  title: string;
  description: string;
  category: string;
  rating: number;
  lessons_count: number;
  lessons_duration: number;
  files: string[];
  is_enrolled: boolean;
  teacher_id: number;
  teacher: {
    first_name: string;
    last_name: string;
    role: string;
    is_active: boolean;
  };
}

export interface PostCourse {
  title: string;
  description: string;
  category: string;
  rating: number;
  lessons_count: number;
  lessons_duration: number;
  files?: string[];
}

export interface CourseSection {
  id: number;
  title: string;
  order: number;
  assignments: CourseAssignment[];
}

export interface CreateUpdateCourseSection {
  title: string;
  order: number;
}

interface AssignmentFile {
  key: string;
  size: number;
  last_modified: string;
  filename: string;
}

export enum CourseAssignmentSubmissionType {
  AutoComplete = "autoComplete",
  WithFile = "fileSubmission",
}

export interface CourseAssignment {
  id: number;
  title: string;
  description: string;
  due_date: string;
  teacher_comments?: string;
  order: number;
  course_id: number;
  section_id: number;
  submission_type: CourseAssignmentSubmissionType;
  is_completed: boolean;
  status: "not_started" | "graded" | "submitted";
  score?: number;
  feedback?: string;
  files: AssignmentFile[];
}

export interface PostCourseReview {
  text: string;
}

export interface CourseReview {
  id: number;
  text: string;
  user_id: number;
  course_id: number;
  created_at: string;
  updated_at: string;
  user_first_name: string;
  user_last_name: string;
}

export interface PostAssignmentGrade {
  score: number;
  feedback: string;
}

export enum CoursePage {
  AllCourses = "allCourses",
  MyCourses = "myCourses",
  CourseDetails = "courseDetails",
}

export interface CourseActionConfig {
  title: string | ReactNode;
  icon?: React.ComponentType;
  link: string;
  buttonProps?: ButtonProps;
  visible: Record<CoursePage, boolean>;
  dynamicParam?: {
    stringToReplace: string;
    propName: keyof GetCourse;
  };
  disabledIfAlreadyEnrolled?: boolean;
  onClick?: (
    courseId: string,
    notification: NotificationInstance
  ) => Promise<boolean>;
}

export type CourseActions = Record<string, CourseActionConfig>;

export type UserAvailableCourseActions = {
  [role: string]: CourseActionConfig[];
};

export type UserAvailableCourseActionsByPage = Record<
  CoursePage,
  UserAvailableCourseActions
>;

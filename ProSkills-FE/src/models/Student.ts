export interface Student {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
}

export interface StudentCourseProgress {
  id: number;
  student_id: number;
  course_id: number;
  completed_assignments: number;
  total_assignments: number;
  last_activity: string;
  completion_percentage: number;
}

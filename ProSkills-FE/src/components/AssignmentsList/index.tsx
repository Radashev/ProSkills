import React, { useEffect, useState } from "react";
import { Collapse, Button, Flex, Space, Tooltip, Upload, message } from "antd";
import {
  CheckCircleOutlined,
  EyeInvisibleOutlined,
  FileSearchOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import { useAssignmentsStore } from "../../store/useAssignmentsStore";
import { useAuthStore } from "../../store/useAuthStore";
import { GUEST_ROLE, UserRoles } from "../../models/User";
import AssignmentItem from "../AssignmentItem";
import AssignmentModal from "../AssignmentModal";
import Loader from "../Loader";
import dayjs from "dayjs";
import { progressApi } from "../../api/progress";
import { notification } from "antd";
import { CourseAssignmentSubmissionType } from "../../models/Course";
import api from "../../api";

interface AssignmentsListProps {
  courseId: number;
  sectionId: number;
  isActive: boolean;
  updateProgress: (newProgress: number) => void;
}

const AssignmentsList: React.FC<AssignmentsListProps> = ({
  courseId,
  sectionId,
  isActive,
  updateProgress,
}) => {
  const role = useAuthStore((state) => state.user?.role) || GUEST_ROLE;
  const { assignments, loading, fetchAssignments, showAddModal } =
    useAssignmentsStore();
  const [completedAssignments, setCompletedAssignments] = useState<Set<number>>(
    new Set()
  );
  const [notificationApi, contextHolder] = notification.useNotification();

  const handleMarkAsDone = async (
    assignmentId: number,
    submissionType: CourseAssignmentSubmissionType,
    file: File | null,
    e: React.MouseEvent<Element, MouseEvent>
  ) => {
    e.stopPropagation();
    try {
      if (submissionType !== CourseAssignmentSubmissionType.AutoComplete) {
        if (!file) {
          message.error("Please upload a file first");
          return;
        }
        const formData = new FormData();
        formData.append("file", file);
        await api.post(
          `/file-storage/assignments/${assignmentId}/submit`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        // Update the assignment status in the store
        useAssignmentsStore.setState((state) => ({
          assignments: state.assignments.map((a) =>
            a.id === assignmentId ? { ...a, status: "submitted" } : a
          ),
        }));
      } else {
        await progressApi.markAsDone(assignmentId.toString());
        setCompletedAssignments((prev) => new Set(prev).add(assignmentId));

        // Calculate and update progress
        const completedCount = assignments.filter(
          (a) =>
            a.is_completed ||
            completedAssignments.has(a.id) ||
            a.id === assignmentId
        ).length;
        const newProgress = +(
          (completedCount / assignments.length) *
          100
        ).toFixed(2);

        updateProgress(newProgress);
      }

      notificationApi.success({
        message: "Success",
        description:
          submissionType === CourseAssignmentSubmissionType.AutoComplete
            ? "Assignment marked as completed"
            : "Assignment sent for review",
        placement: "topRight",
      });
    } catch (error) {
      notificationApi.error({
        message: "Error",
        description:
          submissionType === CourseAssignmentSubmissionType.AutoComplete
            ? "Failed to mark assignment as completed"
            : "Failed to send assignment for review",
        placement: "topRight",
      });
    }
  };

  useEffect(() => {
    const loadAssignments = async () => {
      try {
        if (!isActive) return;

        useAssignmentsStore.setState({ assignments: [], loading: true });
        await fetchAssignments(courseId.toString(), +sectionId);
      } catch (error) {
        console.error("Error loading assignments:", error);
      }
    };

    loadAssignments();
  }, [sectionId, courseId, fetchAssignments, isActive]);

  return (
    <Flex
      vertical
      justify="center"
      align="center"
      style={{ gap: 16, height: "100%" }}
    >
      {contextHolder}
      {role === UserRoles.TEACHER && (
        <Button
          type="primary"
          onClick={() => showAddModal(sectionId)}
          style={{ alignSelf: "flex-end" }}
        >
          Add Assignment
        </Button>
      )}

      {loading ? (
        <Loader />
      ) : assignments.length ? (
        <Collapse
          defaultActiveKey={[]}
          items={assignments.map((assignment) => {
            const today = dayjs();
            const dueDate = dayjs(assignment.due_date);

            const canViewDetails =
              role === UserRoles.TEACHER || today.isBefore(dueDate);
            const isCompleted =
              assignment.is_completed ||
              completedAssignments.has(assignment.id);

            return {
              key: assignment.id.toString(),
              label: (
                <div style={{ textAlign: "left" }}>{assignment.title}</div>
              ),
              extra: (
                <Space>
                  {role === UserRoles.STUDENT && (
                    <>
                      {canViewDetails ? (
                        <>
                          {isCompleted ? (
                            <>
                              {assignment.score && `${assignment.score}/12`}
                              <Tooltip title="Completed">
                                <CheckCircleOutlined
                                  style={{ color: "#52c41a" }}
                                />
                              </Tooltip>
                            </>
                          ) : (
                            <>
                              {assignment.submission_type ===
                                CourseAssignmentSubmissionType.WithFile &&
                                assignment.status === "not_started" && (
                                  <Upload
                                    beforeUpload={(file) => {
                                      handleMarkAsDone(
                                        assignment.id,
                                        assignment.submission_type,
                                        file,
                                        {
                                          stopPropagation: () => {},
                                        } as React.MouseEvent<
                                          Element,
                                          MouseEvent
                                        >
                                      );
                                      return false;
                                    }}
                                    maxCount={1}
                                    showUploadList={false}
                                  >
                                    <Button
                                      size="small"
                                      icon={<UploadOutlined />}
                                    >
                                      Upload & Submit
                                    </Button>
                                  </Upload>
                                )}
                              {assignment.submission_type ===
                                CourseAssignmentSubmissionType.WithFile &&
                                assignment.status === "submitted" && (
                                  <Tooltip title="On review">
                                    <FileSearchOutlined
                                      style={{ color: "#faad14" }}
                                    />
                                  </Tooltip>
                                )}
                              {assignment.submission_type ===
                                CourseAssignmentSubmissionType.AutoComplete && (
                                <Button
                                  type="primary"
                                  size="small"
                                  onClick={(e) =>
                                    handleMarkAsDone(
                                      assignment.id,
                                      assignment.submission_type,
                                      null,
                                      e
                                    )
                                  }
                                >
                                  Done
                                </Button>
                              )}
                            </>
                          )}
                        </>
                      ) : (
                        <Tooltip title="No preview">
                          <EyeInvisibleOutlined style={{ color: "#ff4d4f" }} />
                        </Tooltip>
                      )}
                    </>
                  )}
                </Space>
              ),
              children: <AssignmentItem assignment={assignment} />,
            };
          })}
          style={{ width: "100%" }}
        />
      ) : (
        <Flex justify="center" style={{ width: "100%" }}>
          There're no assignments yet
        </Flex>
      )}
      {role === UserRoles.TEACHER && <AssignmentModal />}
    </Flex>
  );
};

export default React.memo(AssignmentsList, (prevProps, nextProps) => {
  return (
    prevProps.sectionId === nextProps.sectionId &&
    prevProps.courseId === nextProps.courseId &&
    prevProps.isActive === nextProps.isActive
  );
});

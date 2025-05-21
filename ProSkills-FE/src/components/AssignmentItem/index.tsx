import React, { useState } from "react";
import { Button, Flex, Space, Typography, message, theme } from "antd";
import {
  CourseAssignment,
  CourseAssignmentSubmissionType,
} from "../../models/Course";
import { GUEST_ROLE, UserRoles } from "../../models/User";
import { useAuthStore } from "../../store/useAuthStore";
import { useAssignmentsStore } from "../../store/useAssignmentsStore";
import { assignmentFilesApi } from "../../api/files";
import dayjs from "dayjs";
import DeleteModal from "../DeleteModal";
import { useLoaderData } from "react-router";
import { handleFileDownload } from "../../utils/fileUtils";
import TitleComp from "../Title";

const AssignmentItem: React.FC<{ assignment: CourseAssignment }> = ({
  assignment,
}) => {
  const { token: themeToken } = theme.useToken();
  const { courseId } = useLoaderData();
  const role = useAuthStore((state) => state.user?.role) || GUEST_ROLE;

  const { showEditModal, increasePercentDone } = useAssignmentsStore();
  const [showDelete, setShowDelete] = useState(false);

  const today = dayjs();
  const dueDate = dayjs(assignment.due_date);
  const canViewDetails = role === UserRoles.TEACHER || today.isBefore(dueDate);

  const assignmentDetails = [
    { title: "Description", value: assignment.description },
    { title: "Due Date", value: dueDate.format("YYYY-MM-DD") },
    { title: "Teacher Comments", value: assignment.teacher_comments },
    {
      title: "Submission Type",
      value: assignment.submission_type
        ? assignment.submission_type ===
          CourseAssignmentSubmissionType.AutoComplete
          ? "Auto Complete"
          : "File Submission"
        : "Auto Complete",
    },
  ];

  return (
    <>
      {canViewDetails ? (
        <>
          {assignmentDetails.map(
            (el, index) =>
              el.value && (
                <Typography.Paragraph key={index}>
                  <strong>{el.title}:</strong> {el.value}
                </Typography.Paragraph>
              )
          )}
          {assignment.files && assignment.files.length > 0 && (
            <Typography.Paragraph>
              <strong>Files:</strong>
              <br />
              <Space direction="vertical" style={{ marginTop: 8 }}>
                {assignment.files.map((file) => (
                  <Typography.Link
                    key={file.key}
                    onClick={() => handleFileDownload(file.key, file.filename)}
                  >
                    {file.filename} ({(file.size / 1024).toFixed(2)} KB)
                  </Typography.Link>
                ))}
              </Space>
            </Typography.Paragraph>
          )}
          {assignment.feedback && (
            <Typography.Paragraph>
              <TitleComp
                props={{
                  level: 5,
                  style: { color: themeToken.colorPrimaryActive, marginTop: 0 },
                }}
              >
                Feedback by teacher:
              </TitleComp>
              <Typography.Paragraph>{assignment.feedback}</Typography.Paragraph>
            </Typography.Paragraph>
          )}
        </>
      ) : (
        <Typography.Text type="warning">
          This assignment is no longer available for viewing.
        </Typography.Text>
      )}
      {role === UserRoles.TEACHER && (
        <Space>
          <Button type="link" onClick={() => showEditModal(assignment)}>
            Edit
          </Button>
          <Button type="link" danger onClick={() => setShowDelete(true)}>
            Delete
          </Button>
        </Space>
      )}
      {role === UserRoles.TEACHER && showDelete && (
        <DeleteModal
          data={assignment}
          deleteRequest={async () => {
            return new Promise((resolve) => {
              const { deleteAssignment } = useAssignmentsStore.getState();
              deleteAssignment(courseId, assignment.id);
            });
          }}
          onClose={() => setShowDelete(false)}
          onSuccess={() => {}}
        />
      )}
    </>
  );
};

export default AssignmentItem;

import { Form, Input, Button } from "antd";

interface GradeAssignmentFormProps {
  onGradeSubmit: (values: { grade: string; feedback: string }) => void;
}

const GradeAssignmentForm: React.FC<GradeAssignmentFormProps> = ({
  onGradeSubmit,
}) => {
  return (
    <Form layout="inline" onFinish={onGradeSubmit} style={{ width: "100%" }}>
      <Form.Item
        name="grade"
        rules={[
          { required: true, message: "Please input the grade!" },
          {
            pattern: /^(1[0-2]|[1-9])$/,
            message: "Grade must be an integer between 1 and 12",
          },
        ]}
        style={{ flex: 1 }}
      >
        <Input placeholder="Grade (1-12)" type="number" />
      </Form.Item>
      <Form.Item
        name="feedback"
        rules={[{ required: true, message: "Please input feedback!" }]}
        style={{ flex: 2 }}
      >
        <Input placeholder="Feedback" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Grade
        </Button>
      </Form.Item>
    </Form>
  );
};

export default GradeAssignmentForm;

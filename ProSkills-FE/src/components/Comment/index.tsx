import { Card, Typography, Divider, Flex, theme } from "antd";

const Comment: React.FC<{
  author: string;
  content: string;
  createdAt: string;
}> = ({ author, content, createdAt }) => {
  const { token: themeToken } = theme.useToken();

  return (
    <Card style={{ display: "flex", flexDirection: "column" }}>
      <Flex align="center" gap={6}>
        <Typography.Text strong>{author}</Typography.Text>
        <Typography.Text
          style={{
            fontSize: "12px",
            color: themeToken.colorTextDescription,
            lineHeight: "1.5",
          }}
        >
          {createdAt.split("T")[0]}
        </Typography.Text>
      </Flex>
      <Typography.Text
        style={{
          width: "100%",
          textAlign: "left",
          display: "block",
        }}
      >
        {content}
      </Typography.Text>
    </Card>
  );
};

export default Comment;

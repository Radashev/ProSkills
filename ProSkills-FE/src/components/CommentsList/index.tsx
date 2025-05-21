import { Button, Divider, Flex, Input, theme, Typography } from "antd";
import TitleComp from "../Title";
import Comment from "../Comment";
import { CourseReview } from "../../models/Course";

const CommentsList: React.FC<{
  comments: CourseReview[];
  shouldShowAddComment?: boolean;
  onAddComment?: () => void;
  newCommentText?: string;
  onNewCommentTextChange?: (text: string) => void;
}> = ({
  comments,
  shouldShowAddComment = true,
  onAddComment,
  newCommentText = "",
  onNewCommentTextChange,
}) => {
  const { token: themeToken } = theme.useToken();

  return (
    <Flex
      vertical
      justify="center"
      align="center"
      gap={16}
      style={{
        maxWidth: "40rem",
        width: "100%",
        margin: "0 auto",
      }}
    >
      <TitleComp
        props={{
          level: 3,
          style: { color: themeToken.colorPrimaryActive, marginTop: 0 },
        }}
      >
        Comments
      </TitleComp>
      {shouldShowAddComment && (
        <>
          <Input.TextArea
            rows={4}
            style={{ width: "100%" }}
            placeholder="Leave your comment..."
            value={newCommentText}
            onChange={(e) => onNewCommentTextChange?.(e.target.value)}
          />
          <Button
            type="primary"
            style={{ alignSelf: "flex-end" }}
            onClick={onAddComment}
          >
            Add Comment
          </Button>
          <Divider />
        </>
      )}
      <Flex vertical gap={16} style={{ width: "100%" }}>
        {comments.length ? (
          comments.map((comment) => (
            <Comment
              key={comment.id}
              author={`${comment.user_first_name} ${comment.user_last_name}`}
              content={comment.text}
              createdAt={comment.created_at}
            />
          ))
        ) : (
          <Typography.Text>No comments yet</Typography.Text>
        )}
      </Flex>
    </Flex>
  );
};

export default CommentsList;

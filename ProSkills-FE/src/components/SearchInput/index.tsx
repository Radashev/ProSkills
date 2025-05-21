import { Input } from "antd";
import { ChangeEventHandler } from "react";

const { Search } = Input;

const SearchInput: React.FC<{
  onChange: ChangeEventHandler<HTMLInputElement>;
}> = ({ onChange }) => {
  return (
    <Search
      placeholder="Input search text..."
      allowClear
      onChange={onChange}
      style={{ maxWidth: "500px" }}
    />
  );
};

export default SearchInput;

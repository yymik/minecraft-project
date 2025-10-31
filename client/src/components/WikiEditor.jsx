import React, { useRef } from "react";
import PropTypes from "prop-types";
import { Editor } from "@toast-ui/react-editor";
import "@toast-ui/editor/dist/toastui-editor.css";

const WikiEditor = ({ initialValue, onChange }) => {
  const editorRef = useRef(null);

  const handleChange = () => {
    const instance = editorRef.current?.getInstance();
    if (!instance) return;
    onChange(instance.getMarkdown());
  };

  return (
    <Editor
      ref={editorRef}
      height="500px"
      initialEditType="markdown"
      initialValue={initialValue}
      previewStyle="vertical"
      hideModeSwitch
      usageStatistics={false}
      onChange={handleChange}
      toolbarItems={[
        ["heading", "bold", "italic", "strike"],
        ["hr", "quote"],
        ["ul", "ol", "task", "indent", "outdent"],
        ["table", "link"],
        ["code", "codeblock"]
      ]}
    />
  );
};

WikiEditor.propTypes = {
  initialValue: PropTypes.string,
  onChange: PropTypes.func
};

WikiEditor.defaultProps = {
  initialValue: "",
  onChange: () => {}
};

export default WikiEditor;

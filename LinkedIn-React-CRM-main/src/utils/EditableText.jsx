import React, { useEffect, useRef, useState } from 'react';

const EditableText = ({ initialText, save }) => {
  const textRef = useRef(null);
  const [lastSave, setLastSave] = useState(Date.now());

  useEffect(() => {
    if (textRef.current) {
      textRef.current.textContent = initialText;
    }
  }, [initialText]);

  const handleBlur = () => {
    if (textRef.current && textRef.current.textContent !== initialText) {
      const now = Date.now();
      if (now - lastSave > 300) { // Check if last save was more than 300ms ago
        save(textRef.current.textContent);
        setLastSave(now);
      }
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      if (textRef.current && textRef.current.textContent !== initialText) {
        const now = Date.now();
        if (now - lastSave > 300) { // Check if last save was more than 300ms ago
          save(textRef.current.textContent);
          setLastSave(now);
        }
      }
      textRef.current.blur();
    }
  };

  return (
    <div
      ref={textRef}
      contentEditable={true}
      suppressContentEditableWarning={true}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
      style={{
        cursor: 'text',
        outline: 'none',
      }}
    />
  );
};

export default EditableText;

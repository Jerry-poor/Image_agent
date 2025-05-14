
import React, { useState, useEffect } from 'react';

const App = () => {
  // TODO: Replace with actual user ID from authentication context
  const userId = 'user123';

  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState(null);

  // 监听粘贴事件，支持从剪贴板粘贴图片
  useEffect(() => {
    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (items) {
        for (let i = 0; i < items.length; i++) {
          const item = items[i];
          if (item.kind === 'file' && item.type.startsWith('image/')) {
            setImageFile(item.getAsFile());
            break;
          }
        }
      }
    };
    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  // 拖拽上传图片
  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer?.files?.[0];
    if (file) {
      setImageFile(file);
      e.dataTransfer.clearData();
    }
  };
  const handleDragOver = (e) => e.preventDefault();

  // 表单提交
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      alert('请输入文本!');
      return;
    }
    if (!imageFile) {
      alert('请上传图像！');
      return;
    }

    const timestamp = Date.now();
    const queryId = `${userId}_${timestamp}`;

    // 构造 FormData 发送给后端 Agent
    const formData = new FormData();
    formData.append('id', queryId);
    formData.append('text', text);
    formData.append('image', imageFile);

    try {
      const response = await fetch('/api/trigger-agent', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('触发 Agent 失败');
      console.log('Agent 已唤醒，queryId:', queryId);
      // 重置表单
      setText('');
      setImageFile(null);
    } catch (error) {
      console.error('Error triggering agent:', error);
      alert('提交失败，请稍后重试');
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100vw',
        height: '100vh',
        padding: '2rem',
        boxSizing: 'border-box',
        fontFamily: 'Arial, sans-serif',
      }}
    >
      {/* 应用图标 */}
      <img
        src="/icon.png"
        alt="App Icon"
        style={{ width: '64px', height: '64px', marginBottom: '1rem' }}
      />

      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
          maxWidth: '400px',
        }}
      >
        {/* 拖拽/粘贴区 */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          style={{
            width: '100%',
            height: '30vh',
            minHeight: '150px',
            maxHeight: '300px',
            border: '2px dashed #ccc',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            cursor: 'pointer',
            boxSizing: 'border-box',
          }}
        >
          {imageFile ? (
            <img
              src={URL.createObjectURL(imageFile)}
              alt="Preview"
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
            />
          ) : (
            <p>拖拽或粘贴图片到此处</p>
          )}
        </div>

        {/* 文本输入 */}
        <input
          type="text"
          placeholder="请输入描述..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{
            padding: '0.5rem',
            fontSize: '1rem',
            marginBottom: '1rem',
            borderRadius: '4px',
            border: '1px solid #ccc',
            width: '100%',
            boxSizing: 'border-box',
          }}
        />

        {/* 提交按钮 */}
        <button
          type="submit"
          style={{
            padding: '0.75rem',
            fontSize: '1rem',
            borderRadius: '4px',
            backgroundColor: '#4285f4',
            color: '#fff',
            border: 'none',
            cursor: 'pointer',
            width: '100%',
          }}
        >
          提交
        </button>
      </form>
    </div>
  );
};

export default App;


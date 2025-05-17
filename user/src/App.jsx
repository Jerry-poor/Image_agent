import React, { useState, useEffect } from 'react';

const App = () => {
  const userId = 'Jerry520';

  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [latestImgUrl, setLatestImgUrl] = useState(null);

  // 标记“上次服务端图片URL”，只要服务端图片URL没变就不会再弹窗
  const [shownServerImgUrl, setShownServerImgUrl] = useState(null);

  // 粘贴上传
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

  // 拖拽上传
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

    const timestamp = Date.now().toString();
    const uid = userId || 'Jerry520';

    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('requirement', text);
    formData.append('userId', uid);
    formData.append('timestamp', timestamp);

    const host = window.location.hostname;
    const url = `http://${host}:9527/process/`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('触发 Agent 失败');
      setText('');
      setImageFile(null);
      setShownServerImgUrl(null); // 新任务允许检测下一个新图片
    } catch (error) {
      console.error('Error triggering agent:', error);
      alert('提交失败，请稍后重试');
    }
  };

  // 轮询2333端口，弹窗展示新图片
  useEffect(() => {
    let timer;
    let lastBlobUrl = null;
    async function poll() {
      try {
        const res = await fetch('http://localhost:2333/latest-image', { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          // 只要后端图片url和已弹窗的url不一样，才弹窗
          if (data.imageUrl && data.imageUrl !== shownServerImgUrl) {
            const imgRes = await fetch(data.imageUrl + '?t=' + Date.now(), { cache: "no-store" });
            if (imgRes.ok) {
              const blob = await imgRes.blob();
              if (blob.size > 0) {
                // 清理旧blob
                if (lastBlobUrl) URL.revokeObjectURL(lastBlobUrl);
                const url = URL.createObjectURL(blob);
                setLatestImgUrl(url);
                setModalOpen(true);
                setShownServerImgUrl(data.imageUrl); // 标记已弹窗
                lastBlobUrl = url;
              }
            }
          }
        }
      } catch (err) {
        // 忽略网络错误
      } finally {
        timer = setTimeout(poll, 2000);
      }
    }
    poll();
    return () => {
      clearTimeout(timer);
      // 卸载时释放blob
      if (latestImgUrl) URL.revokeObjectURL(latestImgUrl);
    };
    // 只依赖 shownServerImgUrl 保证逻辑正确
  }, [shownServerImgUrl, latestImgUrl]);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100vw',
        minHeight: '100vh',
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

      {/* 弹窗展示生成图片 */}
      {modalOpen && latestImgUrl && (
        <div
          style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.6)',
            zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}
          onClick={() => setModalOpen(false)}
        >
          <div
            style={{
              background: '#fff', padding: 24, borderRadius: 8, boxShadow: '0 2px 8px #0001',
              maxWidth: '80vw', maxHeight: '80vh'
            }}
            onClick={e => e.stopPropagation()}
          >
            <h2>生成图片</h2>
            <img
              src={latestImgUrl}
              alt="生成结果"
              style={{ maxWidth: '100%', maxHeight: '60vh', borderRadius: 4 }}
            />
            <div style={{ textAlign: 'right', marginTop: 16 }}>
              <button onClick={() => setModalOpen(false)}
                style={{ padding: '6px 18px', borderRadius: 4, border: 'none', background: '#4285f4', color: '#fff', fontSize: 16 }}
              >关闭</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;

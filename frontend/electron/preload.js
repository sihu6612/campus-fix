// Preload script — 安全隔离，按需暴露 API 给渲染进程
const { contextBridge } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
})

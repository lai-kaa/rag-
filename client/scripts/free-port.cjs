/**
 * 释放指定端口（Windows），供 npm run dev 启动前调用
 */
const { execSync } = require('child_process')

const port = process.argv[2] || '5173'

if (process.platform !== 'win32') {
  process.exit(0)
}

try {
  const output = execSync(`netstat -ano | findstr :${port}`, { encoding: 'utf8' })
  const pids = new Set()

  for (const line of output.split('\n')) {
    if (!line.includes('LISTENING')) continue
    const parts = line.trim().split(/\s+/)
    const pid = parts[parts.length - 1]
    if (pid && /^\d+$/.test(pid) && pid !== '0') {
      pids.add(pid)
    }
  }

  for (const pid of pids) {
    try {
      execSync(`taskkill /PID ${pid} /F`, { stdio: 'ignore' })
      console.log(`[free-port] 已释放端口 ${port}（PID ${pid}）`)
    } catch {
      // 进程可能已退出
    }
  }
} catch {
  // 端口未被占用
}

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import subprocess, json, os

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            cmd = data.get('command', 'echo hello')
            
            # 【核心修改】指定工作目录为 /tmp，确保文件能写进去
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=15,
                cwd="/tmp" # 强制在可写的临时目录执行
            )
            output = result.stdout + result.stderr
            if not output.strip(): output = "[执行成功，无输出]"
        except subprocess.TimeoutExpired:
            output = "[Error] 命令执行超时（超过15秒）已被强制终止。"
        except Exception as e:
            output = f"[Error] 执行失败: {str(e)}"
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"result": output}).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}...")
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()

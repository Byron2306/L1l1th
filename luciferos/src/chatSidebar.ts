import * as vscode from 'vscode';

export class LuciferOSChatSidebarProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'luciferos.chatSidebar';
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
        };
        webviewView.webview.html = this.getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async (message: any) => {
            if (message.command === 'sendMessage') {
                const userInput = message.text;
                try {
                    const response = await fetch('https://Byron230686-LuciferOS.hf.space/run/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer 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'
                        },
                        body: JSON.stringify({ data: [userInput] })
                    });
                    const data: any = await response.json();
                    webviewView.webview.postMessage({ command: 'showResponse', text: data.data ? data.data[0] : JSON.stringify(data) });
                } catch (err: any) {
                    webviewView.webview.postMessage({ command: 'showResponse', text: 'Error: ' + err });
                }
            }
        });
    }

    private getHtmlForWebview(webview: vscode.Webview): string {
        return `
<html>
  <body style="font-family: sans-serif;">
    <div id="chat" style="height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 8px; margin-bottom: 8px;"></div>
    <input id="input" type="text" style="width: 80%;" placeholder="Type your message..." />
    <button id="send">Send</button>
    <script>
      const vscode = acquireVsCodeApi();
      const chat = document.getElementById('chat');
      document.getElementById('send').onclick = () => {
        const input = document.getElementById('input');
        vscode.postMessage({ command: 'sendMessage', text: input.value });
        chat.innerHTML += '<div><b>You:</b> ' + input.value + '</div>';
        input.value = '';
      };
      window.addEventListener('message', event => {
        const message = event.data;
        if (message.command === 'showResponse') {
          chat.innerHTML += '<div><b>Model:</b> ' + message.text + '</div>';
          chat.scrollTop = chat.scrollHeight;
        }
      });
    </script>
  </body>
</html>
    `;
    }
}

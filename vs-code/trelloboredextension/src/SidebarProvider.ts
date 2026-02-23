import * as vscode from 'vscode';
import * as https from 'https';
import * as http from 'http';
import * as fs from 'fs';
import * as path from 'path';

export class SidebarProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlContent();

        webviewView.webview.onDidReceiveMessage(async message => {
            switch (message.command) {
                case 'fetchChanges':
                    await this._fetchAndDisplayChanges();
                    break;
                case 'saveSettings':
                    await this._saveSettings(message.serverUrl, message.boardUrl);
                    break;
                case 'loadSettings':
                    this._loadSettings();
                    break;
            }
        });
    }

    private async _saveSettings(serverUrl: string, boardUrl: string) {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        await config.update('serverUrl', serverUrl, vscode.ConfigurationTarget.Global);
        await config.update('boardUrl', boardUrl, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('Settings saved!');
    }

    private _loadSettings() {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        const serverUrl = config.get<string>('serverUrl', 'http://localhost:3000');
        const boardUrl = config.get<string>('boardUrl', '');
        this._view?.webview.postMessage({ command: 'settingsLoaded', serverUrl, boardUrl });
    }

    private async _fetchAndDisplayChanges() {
        try {
            const config = vscode.workspace.getConfiguration('trelloboredextension');
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:3000');
            const boardUrl = config.get<string>('boardUrl', '');
            const apiUrl = `${serverUrl}/api/changes${boardUrl ? '?board=' + boardUrl : ''}`;
            const data = await this._httpGet(apiUrl);
            this._view?.webview.postMessage({ command: 'updateChanges', data: JSON.parse(data) });
        } catch (error) {
            this._view?.webview.postMessage({ command: 'error', message: String(error) });
        }
    }

    private _httpGet(url: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const client = url.startsWith('https') ? https : http;
            client.get(url, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve(data));
            }).on('error', reject);
        });
    }

    private _getHtmlContent() {
        const htmlPath = path.join(this._extensionUri.fsPath, 'src', 'sidebar.html');
        return fs.readFileSync(htmlPath, 'utf8');
    }
}

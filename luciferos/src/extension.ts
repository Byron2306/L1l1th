// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import axios from 'axios';
import { LuciferOSChatSidebarProvider } from './chatSidebar';

export function activate(context: vscode.ExtensionContext) {
	console.log('Congratulations, your extension "luciferos" is now active!');

	// Register the chat sidebar provider
	const provider = new LuciferOSChatSidebarProvider(context.extensionUri);
	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider(
			LuciferOSChatSidebarProvider.viewType,
			provider
		)
	);

	// (Optional) Keep the askModel command for command palette
	const disposable = vscode.commands.registerCommand('luciferos.askModel', async () => {
		const userInput = await vscode.window.showInputBox({ prompt: 'Ask LuciferOS (Hugging Face model) a question' });
		if (userInput) {
			try {
				const response = await axios.post(
					'https://api-inference.huggingface.co/models/Byron230686/LuciferOS',
					{ inputs: userInput },
					{
						headers: {
							'Authorization': 'Bearer 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'
						}
					}
				);
				const answer = response.data?.[0]?.generated_text || JSON.stringify(response.data);
				vscode.window.showInformationMessage(answer);
			} catch (error: any) {
				vscode.window.showErrorMessage('Error communicating with the model: ' + (error?.message || error));
			}
		}
	});
	    context.subscriptions.push(disposable);
	}

// This method is called when your extension is deactivated
export function deactivate() {}

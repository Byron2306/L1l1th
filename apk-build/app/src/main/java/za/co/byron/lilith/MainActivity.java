package za.co.byron.lilith;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.webkit.DownloadListener;
import android.webkit.MimeTypeMap;
import android.webkit.SslErrorHandler;
import android.net.http.SslError;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final int FILE_CHOOSER_REQUEST = 7001;
    private static final String PREFS = "lilith_settings";
    private static final String KEY_SERVER = "server_url";

    private WebView webView;
    private ValueCallback<Uri[]> fileChooserCallback;
    private SharedPreferences preferences;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(9, 6, 7));
        getWindow().setNavigationBarColor(Color.rgb(9, 6, 7));

        preferences = getSharedPreferences(PREFS, MODE_PRIVATE);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setUserAgentString(settings.getUserAgentString() + " LILITH-Android/1.0");

        webView.setWebViewClient(new LilithWebViewClient());
        webView.setWebChromeClient(new LilithChromeClient());
        webView.setDownloadListener(new LilithDownloadListener());

        String url = getServerUrl();
        if (url.isEmpty()) showServerDialog(); else webView.loadUrl(url);
    }

    private String normaliseServerUrl(String raw) {
        String value = raw == null ? "" : raw.trim();
        while (value.endsWith("/")) value = value.substring(0, value.length() - 1);
        if (!value.isEmpty() && !(value.startsWith("http://") || value.startsWith("https://"))) {
            value = "http://" + value;
        }
        return value;
    }

    private String getServerUrl() {
        return normaliseServerUrl(preferences.getString(KEY_SERVER, ""));
    }

    private void showServerDialog() {
        EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setHint("http://192.168.1.20:3000");
        input.setText(getServerUrl());
        input.setSelectAllOnFocus(true);
        int padding = (int) (20 * getResources().getDisplayMetrics().density);
        input.setPadding(padding, padding / 2, padding, padding / 2);

        AlertDialog dialog = new AlertDialog.Builder(this)
            .setTitle("Connect LILITH")
            .setMessage("Enter the address of the computer or server running the LILITH Docker stack. Your phone and computer must share a network for a LAN address.")
            .setView(input)
            .setCancelable(false)
            .setPositiveButton("Connect", null)
            .setNegativeButton("Exit", (d, which) -> finish())
            .create();

        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String url = normaliseServerUrl(input.getText().toString());
            if (url.isEmpty()) {
                input.setError("Enter a backend address");
                return;
            }
            preferences.edit().putString(KEY_SERVER, url).apply();
            dialog.dismiss();
            webView.loadUrl(url);
        }));
        dialog.show();
    }

    private class LilithWebViewClient extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            String configured = getServerUrl();
            if (configured.isEmpty() || uri.toString().startsWith(configured)) return false;
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
            } catch (Exception ignored) {
                Toast.makeText(MainActivity.this, "No app can open that link", Toast.LENGTH_SHORT).show();
            }
            return true;
        }

        @Override
        public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
            handler.cancel();
            Toast.makeText(MainActivity.this, "TLS certificate rejected", Toast.LENGTH_LONG).show();
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (request.isForMainFrame()) {
                Toast.makeText(MainActivity.this, "Could not reach LILITH. Press Back to change the server.", Toast.LENGTH_LONG).show();
            }
        }
    }

    private class LilithChromeClient extends WebChromeClient {
        @Override
        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (fileChooserCallback != null) fileChooserCallback.onReceiveValue(null);
            fileChooserCallback = callback;
            Intent intent = params.createIntent();
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            try {
                startActivityForResult(intent, FILE_CHOOSER_REQUEST);
            } catch (Exception ex) {
                fileChooserCallback = null;
                Toast.makeText(MainActivity.this, "No file picker available", Toast.LENGTH_SHORT).show();
                return false;
            }
            return true;
        }
    }

    private class LilithDownloadListener implements DownloadListener {
        @Override
        public void onDownloadStart(String url, String userAgent, String contentDisposition, String mimeType, long contentLength) {
            try {
                String extension = MimeTypeMap.getSingleton().getExtensionFromMimeType(mimeType);
                String filename = "lilith_" + System.currentTimeMillis() + (extension == null ? "" : "." + extension);
                DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                request.setMimeType(mimeType);
                request.addRequestHeader("User-Agent", userAgent);
                request.setTitle(filename);
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename);
                ((DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE)).enqueue(request);
                Toast.makeText(MainActivity.this, "Download started", Toast.LENGTH_SHORT).show();
            } catch (Exception ex) {
                Toast.makeText(MainActivity.this, "Download failed", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST && fileChooserCallback != null) {
            Uri[] result = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
            fileChooserCallback.onReceiveValue(result);
            fileChooserCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) webView.goBack();
        else new AlertDialog.Builder(this)
            .setTitle("LILITH")
            .setItems(new String[]{"Change server", "Close app"}, (dialog, which) -> {
                if (which == 0) showServerDialog(); else finish();
            })
            .show();
    }

    @Override
    protected void onDestroy() {
        if (webView != null) webView.destroy();
        super.onDestroy();
    }
}

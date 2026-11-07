// Hide the extra console window on Windows release builds.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::time::Duration;

/// One message, exactly as defined in docs/api-contract.md (v1).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
struct Message {
    id: i64,
    channel: String,
    sender: String,
    #[serde(default)]
    text: String,
    date: String, // ISO 8601 UTC; the UI formats it in local time
    #[serde(default)]
    has_media: bool,
}

#[derive(Debug, Deserialize)]
struct ApiResponse {
    version: u32,
    messages: Vec<Message>,
}

#[derive(Debug, Deserialize)]
struct ApiErrorBody {
    error: ApiErrorDetail,
}

#[derive(Debug, Deserialize)]
struct ApiErrorDetail {
    code: String,
    message: String,
}

fn api_base() -> String {
    std::env::var("CHAKMAK_API").unwrap_or_else(|_| "http://127.0.0.1:8000".to_string())
}

/// Called from the UI: `invoke("fetch_messages", { limit: 20 })`.
/// Errors are returned as user-readable strings.
#[tauri::command]
async fn fetch_messages(limit: Option<u32>) -> Result<Vec<Message>, String> {
    let limit = limit.unwrap_or(20).clamp(1, 100);
    let url = format!("{}/api/messages?limit={}", api_base(), limit);

    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(10))
        .build()
        .map_err(|e| e.to_string())?;

    let resp = client
        .get(&url)
        .send()
        .await
        .map_err(|e| format!("اتصال به API ناموفق بود ({url}): {e}"))?;

    let status = resp.status();
    if !status.is_success() {
        // Try to show the contract's error message, fall back to the status code.
        let detail = match resp.json::<ApiErrorBody>().await {
            Ok(b) => format!("{}: {}", b.error.code, b.error.message),
            Err(_) => status.to_string(),
        };
        return Err(format!("خطای API — {detail}"));
    }

    let body: ApiResponse = resp
        .json()
        .await
        .map_err(|e| format!("پاسخ API با قرارداد نمی‌خواند: {e}"))?;

    if body.version != 1 {
        return Err(format!("نسخه API پشتیبانی نمی‌شود: {}", body.version));
    }
    Ok(body.messages)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![fetch_messages])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_contract_example() {
        let json = r#"{
            "version": 1, "fetched_at": "2026-11-06T10:00:00Z", "count": 2,
            "messages": [
              {"id": 4821, "channel": "bbcpersian", "sender": "BBC Persian",
               "text": "متن پیام", "date": "2026-11-06T09:58:12Z", "has_media": false},
              {"id": 4820, "channel": "durov", "sender": "Durov's Channel",
               "text": "", "date": "2026-11-06T09:40:00Z", "has_media": true, "extra": 1}
            ]}"#;
        let r: ApiResponse = serde_json::from_str(json).unwrap();
        assert_eq!(r.version, 1);
        assert_eq!(r.messages.len(), 2);
        assert_eq!(r.messages[0].sender, "BBC Persian");
        assert!(r.messages[1].has_media);
    }

    #[test]
    fn missing_text_defaults_to_empty() {
        let m: Message = serde_json::from_str(
            r#"{"id":1,"channel":"c","sender":"s","date":"2026-01-01T00:00:00Z"}"#,
        )
        .unwrap();
        assert_eq!(m.text, "");
        assert!(!m.has_media);
    }
}

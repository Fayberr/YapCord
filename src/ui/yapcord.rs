//! Selects downstream presentation without changing the shared window contract.
use super::*;

/// Used at startup and when the tray recreates the window.
pub(super) fn window() -> Result<YapfastWindow, slint::PlatformError> {
    let window = YapfastWindow::new()?;
    let style = window.global::<ClientStyle>();
    style.set_enabled(!std::env::var("YAPCORD_UI").is_ok_and(|mode| mode == "upstream"));
    if cfg!(windows) {
        style.set_native_font("Segoe UI".into());
    }
    Ok(window)
}

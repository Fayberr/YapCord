//! Selects downstream presentation without changing the shared window contract.
use super::*;

pub(super) fn enabled() -> bool {
    !std::env::var("YAPCORD_UI").is_ok_and(|mode| mode == "upstream")
}

/// Used at startup and when the tray recreates the window.
pub(super) fn window() -> Result<YapfastWindow, slint::PlatformError> {
    let window = YapfastWindow::new()?;
    let style = window.global::<ClientStyle>();
    style.set_enabled(enabled());
    Ok(window)
}

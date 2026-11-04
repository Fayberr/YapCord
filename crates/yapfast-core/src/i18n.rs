//! Interface strings in the chosen language: a small catalog, English complete
//! and other languages as far as translated, with English where a key has no
//! translation.

use std::sync::atomic::{AtomicU8, Ordering};

/// A language the interface can speak.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Language {
    English,
    German,
}

impl Language {
    pub const ALL: [Language; 2] = [Language::English, Language::German];

    /// The language's name in itself, for the settings page.
    pub fn name(self) -> &'static str {
        match self {
            Self::English => "English",
            Self::German => "Deutsch",
        }
    }
}

static CURRENT: AtomicU8 = AtomicU8::new(0);

/// Switches the language every [`tr`] answers in.
pub fn set_language(language: Language) {
    let index = Language::ALL.iter().position(|&l| l == language).unwrap_or(0);
    CURRENT.store(index as u8, Ordering::Relaxed);
}

pub fn language() -> Language {
    Language::ALL[usize::from(CURRENT.load(Ordering::Relaxed)).min(Language::ALL.len() - 1)]
}

/// The text for `key` in the current language.
pub fn tr(key: &str) -> &'static str {
    tr_in(language(), key)
}

/// The text for `key` in `language`, in English when it has none there; an
/// unknown key gives an empty text.
pub fn tr_in(language: Language, key: &str) -> &'static str {
    let found = match language {
        Language::English => None,
        Language::German => german(key),
    };
    found.or_else(|| english(key)).unwrap_or_default()
}

/// `message_hint` for `name`, such as `Message @sam`.
pub fn message_hint(name: &str) -> String {
    tr("message_hint").replace("{name}", name)
}

pub(crate) const KEYS: &[&str] = &[
    "message_hint",
    "view_full_bio",
    "member_since",
    "tab_activity",
    "tab_mutual_friends",
    "tab_mutual_servers",
    "setting_date_format",
    "setting_time_zone",
    "setting_language",
    "date_dmy",
    "date_mdy",
    "date_ymd",
    "zone_system",
    "clock_today_at",
    "clock_yesterday_at",
    "clock_tomorrow_at",
    "clock_last_at",
    "clock_weekday_at",
    "clock_day_at",
];

fn english(key: &str) -> Option<&'static str> {
    Some(match key {
        "message_hint" => "Message @{name}",
        "view_full_bio" => "View full bio",
        "member_since" => "MEMBER SINCE",
        "tab_activity" => "Activity",
        "tab_mutual_friends" => "Mutual friends",
        "tab_mutual_servers" => "Mutual servers",
        "setting_date_format" => "DATE FORMAT",
        "setting_time_zone" => "TIME ZONE",
        "setting_language" => "LANGUAGE",
        "date_dmy" => "Day/Month/Year",
        "date_mdy" => "Month/Day/Year",
        "date_ymd" => "Year-Month-Day",
        "zone_system" => "System default",
        "clock_today_at" => "Today at {time}",
        "clock_yesterday_at" => "Yesterday at {time}",
        "clock_tomorrow_at" => "Tomorrow at {time}",
        "clock_last_at" => "Last {weekday} at {time}",
        "clock_weekday_at" => "{weekday} at {time}",
        "clock_day_at" => "{day} at {time}",
        _ => return None,
    })
}

fn german(key: &str) -> Option<&'static str> {
    Some(match key {
        "message_hint" => "Nachricht an @{name}",
        "view_full_bio" => "Vollständige Bio anzeigen",
        "member_since" => "MITGLIED SEIT",
        "tab_activity" => "Aktivität",
        "tab_mutual_friends" => "Gemeinsame Freunde",
        "tab_mutual_servers" => "Gemeinsame Server",
        "setting_date_format" => "DATUMSFORMAT",
        "setting_time_zone" => "ZEITZONE",
        "setting_language" => "SPRACHE",
        "date_dmy" => "Tag/Monat/Jahr",
        "date_mdy" => "Monat/Tag/Jahr",
        "date_ymd" => "Jahr-Monat-Tag",
        "zone_system" => "Systemstandard",
        "clock_today_at" => "Heute um {time} Uhr",
        "clock_yesterday_at" => "Gestern um {time} Uhr",
        "clock_tomorrow_at" => "Morgen um {time} Uhr",
        "clock_last_at" => "Letzten {weekday} um {time} Uhr",
        "clock_weekday_at" => "{weekday} um {time} Uhr",
        "clock_day_at" => "{day} um {time} Uhr",
        _ => return None,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_german_key_exists_in_english() {
        for key in KEYS {
            assert!(english(key).is_some(), "English lacks {key}");
            if let Some(text) = german(key) {
                assert!(!text.is_empty(), "German {key} is empty");
            }
        }
    }

    #[test]
    fn missing_translations_fall_back_to_english() {
        assert_eq!(tr_in(Language::German, "no_such_key"), "");
        assert_eq!(
            tr_in(Language::German, "view_full_bio"),
            "Vollständige Bio anzeigen"
        );
        assert_eq!(tr_in(Language::English, "tab_activity"), "Activity");
    }

    #[test]
    fn language_is_process_wide_and_fills_names_in() {
        // The process-wide language is left alone, since other tests read it.
        assert_eq!(
            tr_in(Language::German, "message_hint").replace("{name}", "sam"),
            "Nachricht an @sam"
        );
        assert_eq!(message_hint("sam"), "Message @sam");
    }
}

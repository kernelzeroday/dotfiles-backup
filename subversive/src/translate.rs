use std::collections::HashMap;
use std::sync::OnceLock;

fn mock_translations() -> &'static HashMap<&'static str, HashMap<&'static str, &'static str>> {
    static MAP: OnceLock<HashMap<&'static str, HashMap<&'static str, &'static str>>> =
        OnceLock::new();
    MAP.get_or_init(|| {
        let mut map: HashMap<&str, HashMap<&str, &str>> = HashMap::new();

        let mut es = HashMap::new();
        es.insert(
            "The only thing we have to fear is fear itself.",
            "Lo unico que tenemos que temer es al miedo mismo.",
        );
        es.insert(
            "I have nothing to offer but blood, toil, tears and sweat.",
            "No tengo nada que ofrecer sino sangre, esfuerzo, lagrimas y sudor.",
        );
        es.insert("Power is the ultimate aphrodisiac.", "El poder es el afrodisiaco definitivo.");
        map.insert("es", es);

        let mut fr = HashMap::new();
        fr.insert(
            "The illegal we do immediately. The unconstitutional takes a little longer.",
            "L'illegal, nous le faisons immediatement. L'inconstitutionnel prend un peu plus de temps.",
        );
        map.insert("fr", fr);

        let mut de = HashMap::new();
        de.insert(
            "That which does not kill us makes us stronger.",
            "Was uns nicht umbringt, macht uns starker.",
        );
        map.insert("de", de);

        let mut ru = HashMap::new();
        ru.insert(
            "The death of one man is a tragedy, the death of millions is a statistic.",
            "Смерть одного человека — трагедия, смерть миллионов — статистика.",
        );
        map.insert("ru", ru);

        let mut zh = HashMap::new();
        zh.insert(
            "Political power grows out of the barrel of a gun.",
            "枪杆子里出政权。",
        );
        map.insert("zh", zh);

        map
    })
}

pub fn translate_text(text: &str, target_lang: &str) -> String {
    let translations = mock_translations();
    if let Some(lang_map) = translations.get(target_lang) {
        if let Some(translated) = lang_map.get(text) {
            return translated.to_string();
        }
    }
    text.to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_translate_known() {
        let text = "The only thing we have to fear is fear itself.";
        let translated = translate_text(text, "es");
        assert_eq!(
            translated,
            "Lo unico que tenemos que temer es al miedo mismo."
        );

        let text = "Power is the ultimate aphrodisiac.";
        let translated = translate_text(text, "es");
        assert_eq!(translated, "El poder es el afrodisiaco definitivo.");
    }

    #[test]
    fn test_translate_unknown() {
        let text = "This text has no mock translation.";
        let translated = translate_text(text, "es");
        assert_eq!(
            translated, text,
            "Unknown text should return original"
        );
    }

    #[test]
    fn test_translate_invalid_lang() {
        let text = "The only thing we have to fear is fear itself.";
        let translated = translate_text(text, "xx");
        assert_eq!(
            translated, text,
            "Invalid lang should return original"
        );
    }

    #[test]
    fn test_translate_multiple_langs() {
        let text = "The illegal we do immediately. The unconstitutional takes a little longer.";
        let en_original = text;
        let fr = translate_text(text, "fr");
        assert_ne!(
            fr, en_original,
            "French translation should differ from original"
        );
        // Other languages without this quote should return original
        let de = translate_text(text, "de");
        assert_eq!(
            de, en_original,
            "German without this quote should return original"
        );
        let ru = translate_text(text, "ru");
        assert_eq!(
            ru, en_original,
            "Russian without this quote should return original"
        );
    }
}
